import json
from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.services.minio_service import download_json

router = APIRouter(prefix="/api/hasil-dss", tags=["hasil-dss"])


@router.get("/{cabang_id}")
def get_hasil_dss(cabang_id: str):
    db = get_supabase()
    result = (
        db.table("hasil_dss")
        .select("*")
        .eq("cabang_id", cabang_id)
        .order("created_at", desc=True)
        .limit(3)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Belum ada hasil DSS untuk cabang ini")

    output = {}
    for row in result.data:
        bucket, key = row["file_url"].split("/", 1)
        output[row["tipe"]] = download_json(bucket, key)

    return {"cabang_id": cabang_id, "hasil": output}


@router.get("/prediksi/{cabang_id}")
def get_prediksi(cabang_id: str):
    db = get_supabase()
    result = (
        db.table("hasil_dss")
        .select("*")
        .eq("cabang_id", cabang_id)
        .eq("tipe", "prediksi")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Belum ada data prediksi")

    file_url = result.data[0]["file_url"]
    bucket, key = file_url.split("/", 1)
    prediksi = download_json(bucket, key)

    return prediksi


@router.get("/promo/{cabang_id}")
def get_promo(cabang_id: str):
    db = get_supabase()
    result = (
        db.table("hasil_dss")
        .select("*")
        .eq("cabang_id", cabang_id)
        .eq("tipe", "rekomendasi_promo")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Belum ada data rekomendasi promo")

    file_url = result.data[0]["file_url"]
    bucket, key = file_url.split("/", 1)
    promo = download_json(bucket, key)

    return promo


@router.get("/engineering/{cabang_id}")
def get_engineering(cabang_id: str):
    db = get_supabase()
    result = (
        db.table("hasil_dss")
        .select("*")
        .eq("cabang_id", cabang_id)
        .eq("tipe", "menu_engineering")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Belum ada data menu engineering")

    file_url = result.data[0]["file_url"]
    bucket, key = file_url.split("/", 1)
    data = download_json(bucket, key)

    return {
        "cabang_id": cabang_id,
        "periode_minggu": data.get("periode_minggu"),
        "generated_at": data.get("generated_at"),
        "menu_engineering": data.get("menu_engineering", {}),
    }
