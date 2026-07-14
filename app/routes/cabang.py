from fastapi import APIRouter, HTTPException
from app.models.schemas import CabangCreate
from app.database import get_supabase

router = APIRouter(prefix="/api/cabang", tags=["cabang"])


@router.post("")
def create_cabang(data: CabangCreate):
    db = get_supabase()

    existing = db.table("cabang").select("id").eq("id", data.id).execute()
    if existing.data:
        return {"error": f"Cabang dengan id '{data.id}' sudah ada"}

    result = db.table("cabang").insert({
        "id": data.id,
        "nama": data.nama,
        "lokasi": data.lokasi,
    }).execute()

    return {"message": "Cabang berhasil dibuat", "data": result.data[0]}


@router.get("")
def get_all_cabang():
    db = get_supabase()
    result = db.table("cabang").select("*").execute()
    return {"data": result.data}


@router.get("/{cabang_id}")
def get_cabang(cabang_id: str):
    db = get_supabase()
    result = db.table("cabang").select("*").eq("id", cabang_id).execute()
    if not result.data:
        return {"error": "Cabang tidak ditemukan"}
    return {"data": result.data[0]}
