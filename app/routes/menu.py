from fastapi import APIRouter
from app.database import get_supabase

router = APIRouter(prefix="/api/menu", tags=["menu"])


@router.get("")
def get_all_menu():
    db = get_supabase()
    result = db.table("menu").select("id, nama, harga").order("id").execute()
    return {"count": len(result.data), "data": result.data}
