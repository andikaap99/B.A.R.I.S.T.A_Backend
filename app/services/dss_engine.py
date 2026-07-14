import pickle
import logging
from datetime import date, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from app.services.transaksi_service import get_all_transaksi_mingguan
from app.services.minio_service import upload_json, download_model_pkl
from app.database import get_supabase

logger = logging.getLogger(__name__)

HARI_INDONESIA = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu",
}

CABANG_TO_STORE = {
    "cabang_1": "Astoria",
    "cabang_2": "Hell's Kitchen",
    "cabang_3": "Lower Manhattan",
}


def run_dss_engine():
    logger.info("=== DSS Engine Start ===")
    try:
        transaksi_data = get_all_transaksi_mingguan()
        if not transaksi_data:
            logger.warning("Tidak ada data transaksi 7 hari terakhir")
            return

        df = pd.DataFrame(transaksi_data)
        cabang_ids = df["cabang_id"].unique().tolist()

        model_bytes = download_model_pkl()
        model_dict = pickle.loads(model_bytes)

        db = get_supabase()
        today = date.today()
        periode_minggu = today.isoformat()

        for cabang_id in cabang_ids:
            try:
                _process_cabang(cabang_id, df, model_dict, db, today, periode_minggu)
            except Exception as e:
                logger.error(f"Error processing {cabang_id}: {e}")

        logger.info("=== DSS Engine Selesai ===")

    except Exception as e:
        logger.error(f"DSS Engine error: {e}")


def _process_cabang(cabang_id: str, df: pd.DataFrame, model_dict, db, today: date, periode_minggu: str):
    cabang_df = df[df["cabang_id"] == cabang_id].copy()

    aggregated = (
        cabang_df.groupby(["tanggal", "menu"])["qty"]
        .sum()
        .reset_index()
    )

    pivot = aggregated.pivot(index="tanggal", columns="menu", values="qty").fillna(0)
    pivot = pivot.sort_index()

    menus = pivot.columns.tolist()
    last_7 = pivot.tail(7)

    if len(last_7) < 7:
        while len(last_7) < 7:
            last_7 = pd.concat([pd.DataFrame([{}], columns=menus, index=[last_7.index.min() - timedelta(days=1)]), last_7])

    store_name = CABANG_TO_STORE.get(cabang_id)
    store_models = model_dict.get(store_name, {}) if isinstance(model_dict, dict) else {}

    menu_prices = {}
    for menu_nama in menus:
        price_result = db.table("menu").select("harga").eq("nama", menu_nama).execute()
        if price_result.data:
            menu_prices[menu_nama] = float(price_result.data[0]["harga"])
        else:
            menu_prices[menu_nama] = 0.0

    prediksi_list = []
    for menu in menus:
        menu_info = store_models.get(menu)
        if menu_info and "model" in menu_info:
            menu_model = menu_info["model"]
            last_day_index = menu_info["last_day_index"]
            last_date = menu_info["last_date"]
            if isinstance(last_date, str):
                last_date = pd.Timestamp(last_date)

            feature_day_index = []
            feature_day_of_week = []
            for i in range(7):
                future_date = last_date + timedelta(days=i + 1)
                feature_day_index.append(last_day_index + i + 1)
                feature_day_of_week.append(future_date.weekday())
            future_X = np.column_stack([feature_day_index, feature_day_of_week])
            predicted = menu_model.predict(future_X)
        else:
            X = np.arange(len(last_7)).reshape(-1, 1)
            y = last_7[menu].values
            menu_model = LinearRegression()
            menu_model.fit(X, y)
            future_X = np.arange(len(last_7), len(last_7) + 7).reshape(-1, 1)
            predicted = menu_model.predict(future_X)

        for i, qty in enumerate(predicted):
            prediksi_date = today + timedelta(days=i + 1)
            prediksi_list.append({
                "menu": menu,
                "prediksi_qty": round(float(max(0, qty)), 2),
                "tanggal": prediksi_date.isoformat(),
            })

    menu_engineering = _calculate_menu_engineering(prediksi_list, menu_prices, menus)

    promo_list = _generate_dynamic_promo(prediksi_list, menu_prices, menu_engineering, today)

    _save_promo_to_db(db, cabang_id, promo_list, periode_minggu)

    prediksi_data = {
        "cabang_id": cabang_id,
        "periode_minggu": periode_minggu,
        "generated_at": f"{periode_minggu}T23:00:00",
        "prediksi": prediksi_list,
    }

    file_url = upload_json("dss-results", f"hasil_{cabang_id}_{periode_minggu}.json", {
        **prediksi_data,
        "menu_engineering": menu_engineering,
        "rekomendasi_promo": promo_list,
    })

    db.table("hasil_dss").delete().eq("cabang_id", cabang_id).execute()

    db.table("hasil_dss").insert({
        "periode_minggu": periode_minggu,
        "cabang_id": cabang_id,
        "tipe": "prediksi",
        "file_url": file_url,
    }).execute()

    db.table("hasil_dss").insert({
        "periode_minggu": periode_minggu,
        "cabang_id": cabang_id,
        "tipe": "rekomendasi_promo",
        "file_url": file_url,
    }).execute()

    db.table("hasil_dss").insert({
        "periode_minggu": periode_minggu,
        "cabang_id": cabang_id,
        "tipe": "menu_engineering",
        "file_url": file_url,
    }).execute()

    logger.info(f"Selesai proses {cabang_id}")


def _calculate_menu_engineering(prediksi_list: list, menu_prices: dict, menus: list) -> dict:
    menu_avg_prediksi = {}
    for menu in menus:
        menu_preds = [p["prediksi_qty"] for p in prediksi_list if p["menu"] == menu]
        menu_avg_prediksi[menu] = np.mean(menu_preds) if menu_preds else 0

    total_prediksi = sum(menu_avg_prediksi.values())
    avg_prediksi = total_prediksi / len(menus) if menus else 0

    menu_profit = {}
    for menu in menus:
        menu_profit[menu] = menu_prices.get(menu, 0) * menu_avg_prediksi.get(menu, 0)

    total_profit = sum(menu_profit.values())
    avg_profit = total_profit / len(menus) if menus else 0

    engineering = {"star": [], "plowhorse": [], "puzzle": [], "dog": []}

    for menu in menus:
        high_popularity = menu_avg_prediksi.get(menu, 0) >= avg_prediksi
        high_profitability = menu_profit.get(menu, 0) >= avg_profit

        if high_popularity and high_profitability:
            engineering["star"].append(menu)
        elif high_popularity and not high_profitability:
            engineering["plowhorse"].append(menu)
        elif not high_popularity and high_profitability:
            engineering["puzzle"].append(menu)
        else:
            engineering["dog"].append(menu)

    return engineering


def _generate_dynamic_promo(prediksi_list: list, menu_prices: dict, menu_engineering: dict, today: date) -> list:
    promo_candidates = menu_engineering.get("puzzle", []) + menu_engineering.get("dog", [])

    if not promo_candidates:
        return []

    daily_prediksi = {}
    for item in prediksi_list:
        tgl = item["tanggal"]
        if tgl not in daily_prediksi:
            daily_prediksi[tgl] = []
        daily_prediksi[tgl].append(item)

    promo_list = []
    candidate_index = 0

    for i in range(7):
        prediksi_date = today + timedelta(days=i + 1)
        tgl_str = prediksi_date.isoformat()

        if tgl_str in daily_prediksi:
            hari_prediksi = sorted(daily_prediksi[tgl_str], key=lambda x: x["prediksi_qty"])

            if hari_prediksi:
                selected_menu = promo_candidates[candidate_index % len(promo_candidates)]
                candidate_index += 1

                menu_preds = [p for p in hari_prediksi if p["menu"] == selected_menu]
                if not menu_preds:
                    selected_menu = hari_prediksi[0]["menu"]

                kuadran = "Puzzle" if selected_menu in menu_engineering.get("puzzle", []) else "Dog"
                harga_normal = menu_prices.get(selected_menu, 0)

                if kuadran == "Puzzle":
                    diskon_pct = 10
                else:
                    diskon_pct = 20

                harga_promo = harga_normal * (1 - diskon_pct / 100)

                if kuadran == "Puzzle":
                    alasan = "Prediksi penjualan rendah, margin tinggi"
                else:
                    alasan = "Prediksi penjualan rendah, margin rendah"

                promo_list.append({
                    "hari": HARI_INDONESIA[prediksi_date.weekday()],
                    "tanggal": tgl_str,
                    "menu": selected_menu,
                    "kuadran": kuadran,
                    "harga_normal": harga_normal,
                    "diskon": f"{diskon_pct}%",
                    "harga_promo": round(harga_promo, 2),
                    "alasan": alasan,
                })

    return promo_list


def _save_promo_to_db(db, cabang_id: str, promo_list: list, periode_minggu: str):
    db.table("promo").delete().eq("cabang_id", cabang_id).eq("periode_minggu", periode_minggu).execute()

    for promo in promo_list:
        db.table("promo").insert({
            "cabang_id": cabang_id,
            "menu_nama": promo["menu"],
            "kuadran": promo["kuadran"],
            "harga_normal": promo["harga_normal"],
            "diskon": promo["diskon"],
            "harga_promo": promo["harga_promo"],
            "kuota": 20,
            "terpakai": 0,
            "is_active": True,
            "periode_minggu": periode_minggu,
        }).execute()
