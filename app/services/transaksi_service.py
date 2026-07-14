from datetime import date, timedelta
from app.database import get_supabase


def _get_harga_menu(db, menu_nama: str) -> int:
    result = db.table("menu").select("harga").eq("nama", menu_nama).execute()
    if result.data:
        return result.data[0]["harga"]
    raise ValueError(f"Menu '{menu_nama}' tidak ditemukan di tabel menu")


def _get_active_promo(db, cabang_id: str, menu_nama: str):
    today = date.today().isoformat()
    result = (
        db.table("promo")
        .select("*")
        .eq("cabang_id", cabang_id)
        .eq("menu_nama", menu_nama)
        .eq("is_active", True)
        .lte("periode_minggu", today)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        promo = result.data[0]
        if promo.get("terpakai", 0) < promo.get("kuota", 20):
            return promo
    return None


def _increment_promo_used(db, promo_id: str):
    result = db.table("promo").select("terpakai").eq("id", promo_id).execute()
    if result.data:
        current = result.data[0].get("terpakai", 0)
        db.table("promo").update({"terpakai": current + 1}).eq("id", promo_id).execute()


def create_transaksi(cabang_id: str, tanggal: date, items: list[dict]):
    db = get_supabase()
    rows = []
    for item in items:
        harga_normal = _get_harga_menu(db, item["menu"])
        promo = _get_active_promo(db, cabang_id, item["menu"])

        if promo:
            harga = round(float(promo["harga_promo"]))
            keterangan = True
            _increment_promo_used(db, promo["id"])
        else:
            harga = round(float(harga_normal))
            keterangan = False

        rows.append({
            "cabang_id": cabang_id,
            "menu": item["menu"],
            "qty": item["qty"],
            "harga": harga,
            "keterangan": keterangan,
            "tanggal": tanggal.isoformat(),
        })

    result = db.table("transaksi").insert(rows).execute()
    return result.data


def get_transaksi_by_cabang(cabang_id: str):
    db = get_supabase()
    result = db.table("transaksi").select("*").eq("cabang_id", cabang_id).order("tanggal", desc=True).execute()
    return result.data


def get_transaksi_mingguan(cabang_id: str):
    db = get_supabase()
    today = date.today()
    seven_days_ago = today - timedelta(days=7)
    result = (
        db.table("transaksi")
        .select("*")
        .eq("cabang_id", cabang_id)
        .gte("tanggal", seven_days_ago.isoformat())
        .lte("tanggal", today.isoformat())
        .order("tanggal", desc=False)
        .execute()
    )
    return result.data


def get_all_transaksi_mingguan():
    db = get_supabase()
    today = date.today()
    seven_days_ago = today - timedelta(days=7)
    result = (
        db.table("transaksi")
        .select("*")
        .gte("tanggal", seven_days_ago.isoformat())
        .lte("tanggal", today.isoformat())
        .order("tanggal", desc=False)
        .execute()
    )
    return result.data
