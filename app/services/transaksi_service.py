from datetime import date, timedelta
from app.database import get_supabase


def create_transaksi(cabang_id: str, menu: str, qty: int, harga: float, tanggal: date):
    db = get_supabase()
    result = db.table("transaksi").insert({
        "cabang_id": cabang_id,
        "menu": menu,
        "qty": qty,
        "harga": harga,
        "tanggal": tanggal.isoformat(),
    }).execute()
    return result.data[0]


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
