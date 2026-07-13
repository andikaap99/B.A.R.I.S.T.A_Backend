from datetime import date, timedelta
from fastapi import APIRouter
from app.database import get_supabase
from app.services.minio_service import download_json

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/semua-cabang")
def get_semua_cabang():
    db = get_supabase()
    cabang_result = db.table("cabang").select("*").execute()
    cabang_list = cabang_result.data

    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    output = []
    for cabang in cabang_list:
        transaksi = (
            db.table("transaksi")
            .select("*")
            .eq("cabang_id", cabang["id"])
            .gte("tanggal", seven_days_ago.isoformat())
            .lte("tanggal", today.isoformat())
            .execute()
        ).data

        total_revenue = sum(float(t["qty"]) * float(t["harga"]) for t in transaksi)
        total_transaksi = len(transaksi)

        menu_count = {}
        for t in transaksi:
            menu_count[t["menu"]] = menu_count.get(t["menu"], 0) + int(t["qty"])
        top_menu = max(menu_count, key=menu_count.get) if menu_count else "-"

        output.append({
            "cabang_id": cabang["id"],
            "nama": cabang["nama"],
            "total_revenue": total_revenue,
            "total_transaksi": total_transaksi,
            "top_menu": top_menu,
        })

    return {"periode": "7 hari terakhir", "data": output}


@router.get("/perbandingan")
def get_perbandingan():
    db = get_supabase()
    cabang_result = db.table("cabang").select("*").execute()

    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    output = []
    for cabang in cabang_result.data:
        transaksi = (
            db.table("transaksi")
            .select("*")
            .eq("cabang_id", cabang["id"])
            .gte("tanggal", seven_days_ago.isoformat())
            .lte("tanggal", today.isoformat())
            .execute()
        ).data

        revenue = sum(float(t["qty"]) * float(t["harga"]) for t in transaksi)

        menu_count = {}
        for t in transaksi:
            menu_count[t["menu"]] = menu_count.get(t["menu"], 0) + int(t["qty"])
        menu_terlaris = max(menu_count, key=menu_count.get) if menu_count else "-"

        output.append({
            "cabang_id": cabang["id"],
            "nama": cabang["nama"],
            "revenue_mingguan": revenue,
            "transaksi_mingguan": len(transaksi),
            "menu_terlaris": menu_terlaris,
        })

    return {"periode": "7 hari terakhir", "data": output}


@router.get("/hasil-dss-global")
def get_hasil_dss_global():
    db = get_supabase()
    cabang_result = db.table("cabang").select("*").execute()

    output = []
    for cabang in cabang_result.data:
        result = (
            db.table("hasil_dss")
            .select("*")
            .eq("cabang_id", cabang["id"])
            .order("created_at", desc=True)
            .limit(2)
            .execute()
        ).data

        dss = {}
        for row in result:
            bucket, key = row["file_url"].split("/", 1)
            dss[row["tipe"]] = download_json(bucket, key)

        output.append({
            "cabang_id": cabang["id"],
            "nama": cabang["nama"],
            "hasil_dss": dss,
        })

    return {"data": output}
