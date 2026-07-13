import pickle
import logging
from datetime import date, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from app.services.transaksi_service import get_all_transaksi_mingguan
from app.services.minio_service import upload_prediksi, upload_promo, download_model_pkl
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

    prediksi_data = {
        "cabang_id": cabang_id,
        "periode_minggu": periode_minggu,
        "generated_at": f"{periode_minggu}T23:00:00",
        "prediksi": prediksi_list,
    }

    file_url = upload_prediksi(cabang_id, periode_minggu, prediksi_data)
    db.table("hasil_dss").insert({
        "periode_minggu": periode_minggu,
        "cabang_id": cabang_id,
        "tipe": "prediksi",
        "file_url": file_url,
    }).execute()

    promo_list = _generate_promo(prediksi_list, menus, today)
    promo_data = {
        "cabang_id": cabang_id,
        "periode_minggu": periode_minggu,
        "generated_at": f"{periode_minggu}T23:00:00",
        "rekomendasi_promo": promo_list,
    }

    promo_url = upload_promo(cabang_id, periode_minggu, promo_data)
    db.table("hasil_dss").insert({
        "periode_minggu": periode_minggu,
        "cabang_id": cabang_id,
        "tipe": "rekomendasi_promo",
        "file_url": promo_url,
    }).execute()

    logger.info(f"Selesai proses {cabang_id}")


def _generate_promo(prediksi_list: list, menus: list, today: date) -> list:
    promo = []
    daily_prediksi = {}
    for item in prediksi_list:
        tgl = item["tanggal"]
        if tgl not in daily_prediksi:
            daily_prediksi[tgl] = []
        daily_prediksi[tgl].append(item)

    for i in range(7):
        prediksi_date = today + timedelta(days=i + 1)
        tgl_str = prediksi_date.isoformat()

        if tgl_str in daily_prediksi:
            hari_prediksi = sorted(daily_prediksi[tgl_str], key=lambda x: x["prediksi_qty"])
            if hari_prediksi:
                promo.append({
                    "hari": HARI_INDONESIA[prediksi_date.weekday()],
                    "tanggal": tgl_str,
                    "menu": hari_prediksi[0]["menu"],
                    "alasan": "prediksi penjualan terendah",
                })

    return promo
