from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import UserCreate, UserLogin
from app.services.auth_service import register_user, login_user
from app.logging_config import log_security_event

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(request: Request, data: UserCreate):
    ip = request.client.host if request.client else "-"
    result = register_user(
        username=data.username,
        password=data.password,
        cabang_id=data.cabang_id,
    )
    if "error" in result:
        log_security_event(
            event_type="REGISTER",
            actor=data.username,
            result="FAILED",
            ip=ip,
            resource="/api/auth/register",
            detail=result["error"]
        )
        raise HTTPException(status_code=400, detail=result["error"])

    log_security_event(
        event_type="REGISTER",
        actor=data.username,
        result="SUCCESS",
        ip=ip,
        resource="/api/auth/register"
    )
    return result


@router.post("/login")
def login(request: Request, data: UserLogin):
    ip = request.client.host if request.client else "-"
    result = login_user(
        username=data.username,
        password=data.password,
    )
    if "error" in result:
        log_security_event(
            event_type="LOGIN",
            actor=data.username,
            result="FAILED",
            ip=ip,
            resource="/api/auth/login",
            detail=result["error"]
        )
        raise HTTPException(status_code=401, detail=result["error"])

    log_security_event(
        event_type="LOGIN",
        actor=data.username,
        result="SUCCESS",
        ip=ip,
        resource="/api/auth/login"
    )
    return result
