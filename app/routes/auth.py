from fastapi import APIRouter, HTTPException
from app.models.schemas import UserCreate, UserLogin
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(data: UserCreate):
    result = register_user(
        username=data.username,
        password=data.password,
        cabang_id=data.cabang_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/login")
def login(data: UserLogin):
    result = login_user(
        username=data.username,
        password=data.password,
    )
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result
