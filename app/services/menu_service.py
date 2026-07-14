import pickle
import logging
from datetime import date
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from app.database import get_supabase
from app.services.minio_service import download_model, upload_model_pkl

logger = logging.getLogger(__name__)

CABANG_IDS = ["cabang_1", "cabang_2", "cabang_3"]


def get_all_menu():
    db = get_supabase()
    result = db.table("menu").select("*").eq("is_active", True).order("id").execute()
    return result.data


def get_menu_by_id(menu_id: str):
    db = get_supabase()
    result = db.table("menu").select("*").eq("id", menu_id).execute()
    if not result.data:
        return None
    return result.data[0]


def get_menu_by_nama(nama: str):
    db = get_supabase()
    result = db.table("menu").select("*").eq("nama", nama).execute()
    if not result.data:
        return None
    return result.data[0]


def create_menu(nama: str, kategori: str, harga: float):
    db = get_supabase()
    existing = db.table("menu").select("id").eq("nama", nama).execute()
    if existing.data:
        return {"error": f"Menu '{nama}' sudah ada"}

    result = db.table("menu").insert({
        "nama": nama,
        "kategori": kategori,
        "harga": harga,
        "is_active": True,
    }).execute()
    return {"data": result.data[0]}


def update_menu(menu_id: str, nama: str | None = None, kategori: str | None = None, harga: float | None = None):
    db = get_supabase()
    menu = get_menu_by_id(menu_id)
    if not menu:
        return {"error": "Menu tidak ditemukan"}

    update_data = {}
    old_nama = menu["nama"]

    if nama is not None:
        existing = db.table("menu").select("id").eq("nama", nama).neq("id", menu_id).execute()
        if existing.data:
            return {"error": f"Menu '{nama}' sudah digunakan"}
        update_data["nama"] = nama
    if kategori is not None:
        update_data["kategori"] = kategori
    if harga is not None:
        update_data["harga"] = harga

    if not update_data:
        return {"error": "Tidak ada data yang diupdate"}

    result = db.table("menu").update(update_data).eq("id", menu_id).execute()

    if nama is not None and nama != old_nama:
        _rename_menu_in_model(old_nama, nama)

    return {"data": result.data[0]}


def delete_menu(menu_id: str):
    db = get_supabase()
    menu = get_menu_by_id(menu_id)
    if not menu:
        return {"error": "Menu tidak ditemukan"}

    db.table("menu").update({"is_active": False}).eq("id", menu_id).execute()
    _remove_menu_from_model(menu["nama"])
    return {"message": f"Menu '{menu['nama']}' berhasil dihapus (soft delete)"}


def _rename_menu_in_model(old_nama: str, new_nama: str):
    try:
        model_bytes = download_model()
        model_dict = pickle.loads(model_bytes)

        for store_name in model_dict:
            if old_nama in model_dict[store_name]:
                model_dict[store_name][new_nama] = model_dict[store_name].pop(old_nama)

        upload_model_pkl(model_dict)
        logger.info(f"Renamed menu in model.pkl: {old_nama} -> {new_nama}")
    except Exception as e:
        logger.error(f"Gagal rename menu in model.pkl: {e}")


def _remove_menu_from_model(menu_nama: str):
    try:
        model_bytes = download_model()
        model_dict = pickle.loads(model_bytes)

        for store_name in list(model_dict.keys()):
            if menu_nama in model_dict[store_name]:
                del model_dict[store_name][menu_nama]

        upload_model_pkl(model_dict)
        logger.info(f"Removed menu from model.pkl: {menu_nama}")
    except Exception as e:
        logger.error(f"Gagal hapus menu from model.pkl: {e}")


def train_menu(menu_nama: str):
    db = get_supabase()
    menu = get_menu_by_nama(menu_nama)
    if not menu:
        return {"error": f"Menu '{menu_nama}' tidak ditemukan"}

    result = db.table("transaksi").select("*").eq("menu", menu_nama).execute()
    transaksi_data = result.data

    if not transaksi_data:
        return {"error": f"Tidak ada data transaksi untuk menu '{menu_nama}'"}

    df = pd.DataFrame(transaksi_data)
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    try:
        model_bytes = download_model()
        model_dict = pickle.loads(model_bytes)
    except Exception:
        model_dict = {}

    trained_count = 0
    for cabang_id in CABANG_IDS:
        cabang_df = df[df["cabang_id"] == cabang_id].copy()
        if len(cabang_df) < 7:
            logger.warning(f"SKIP: {cabang_id} - {menu_nama} (data kurang: {len(cabang_df)} hari)")
            continue

        daily = cabang_df.groupby("tanggal")["qty"].sum().reset_index()
        daily = daily.sort_values("tanggal")
        daily["day_index"] = range(len(daily))
        daily["day_of_week"] = daily["tanggal"].dt.dayofweek

        X = daily[["day_index", "day_of_week"]].values
        y = daily["qty"].values

        model = LinearRegression()
        model.fit(X, y)

        if cabang_id not in model_dict:
            model_dict[cabang_id] = {}

        model_dict[cabang_id][menu_nama] = {
            "model": model,
            "last_day_index": daily["day_index"].max(),
            "last_date": daily["tanggal"].max(),
        }
        trained_count += 1

    upload_model_pkl(model_dict)

    total_models = sum(len(v) for v in model_dict.values())
    return {
        "message": f"Berhasil train menu '{menu_nama}'",
        "trained_cabang": trained_count,
        "total_models_in_pkl": total_models,
    }


def train_all_menus():
    db = get_supabase()
    menus = db.table("menu").select("nama").eq("is_active", True).execute()
    menu_names = [m["nama"] for m in menus.data]

    results = []
    for menu_nama in menu_names:
        result = train_menu(menu_nama)
        results.append({"menu": menu_nama, **result})

    success = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]
    return {
        "message": f"Training selesai: {len(success)} sukses, {len(errors)} gagal",
        "results": results,
    }


def get_train_status():
    try:
        model_bytes = download_model()
        model_dict = pickle.loads(model_bytes)
    except Exception:
        model_dict = {}

    db = get_supabase()
    menus = db.table("menu").select("nama").eq("is_active", True).execute()
    menu_names = [m["nama"] for m in menus.data]

    menus_status = []
    trained_count = 0
    for menu_nama in menu_names:
        has_model = False
        for store_models in model_dict.values():
            if menu_nama in store_models:
                has_model = True
                break
        if has_model:
            trained_count += 1
        menus_status.append({"menu": menu_nama, "has_model": has_model})

    return {
        "total_menu": len(menu_names),
        "trained": trained_count,
        "untrained": len(menu_names) - trained_count,
        "menus": menus_status,
    }
