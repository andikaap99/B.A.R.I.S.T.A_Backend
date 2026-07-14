from fastapi import APIRouter, HTTPException
from app.database import get_supabase

router = APIRouter(prefix="/api/promo", tags=["promo"])


@router.get("/{cabang_id}")
def get_active_promo(cabang_id: str):
    db = get_supabase()
    result = (
        db.table("promo")
        .select("*")
        .eq("cabang_id", cabang_id)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return {"cabang_id": cabang_id, "count": len(result.data), "data": result.data}
