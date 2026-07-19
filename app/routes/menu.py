from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import MenuCreate, MenuUpdate
from app.services.menu_service import (
    get_all_menu,
    get_inactive_menu,
    get_menu_by_id,
    create_menu,
    update_menu,
    delete_menu,
    activate_menu,
    train_menu,
    train_all_menus,
    get_train_status,
)
from app.logging_config import log_security_event

router = APIRouter(prefix="/api/menu", tags=["menu"])


@router.get("")
def get_all_menu_endpoint():
    data = get_all_menu()
    return {"count": len(data), "data": data}


@router.get("/inactive")
def get_inactive_menu_endpoint():
    data = get_inactive_menu()
    return {"count": len(data), "data": data}


@router.get("/{menu_id}")
def get_menu_endpoint(menu_id: str):
    data = get_menu_by_id(menu_id)
    if not data:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan")
    return {"data": data}


@router.post("")
def create_menu_endpoint(request: Request, data: MenuCreate):
    ip = request.client.host if request.client else "-"
    result = create_menu(nama=data.nama, kategori=data.kategori, harga=data.harga)
    if "error" in result:
        log_security_event(
            event_type="CREATE_MENU",
            actor="system",
            result="FAILED",
            ip=ip,
            resource="/api/menu",
            detail=result["error"]
        )
        raise HTTPException(status_code=400, detail=result["error"])

    log_security_event(
        event_type="CREATE_MENU",
        actor="system",
        result="SUCCESS",
        ip=ip,
        resource="/api/menu",
        detail=f"Menu: {data.nama}"
    )
    return {"message": "Menu berhasil dibuat", "data": result["data"]}


@router.put("/{menu_id}")
def update_menu_endpoint(request: Request, menu_id: str, data: MenuUpdate):
    ip = request.client.host if request.client else "-"
    result = update_menu(
        menu_id=menu_id,
        nama=data.nama,
        kategori=data.kategori,
        harga=data.harga,
    )
    if "error" in result:
        log_security_event(
            event_type="UPDATE_MENU",
            actor="system",
            result="FAILED",
            ip=ip,
            resource=f"/api/menu/{menu_id}",
            detail=result["error"]
        )
        raise HTTPException(status_code=400, detail=result["error"])

    log_security_event(
        event_type="UPDATE_MENU",
        actor="system",
        result="SUCCESS",
        ip=ip,
        resource=f"/api/menu/{menu_id}",
        detail=f"Updated: {data.nama or menu_id}"
    )
    return {"message": "Menu berhasil diupdate", "data": result["data"]}


@router.delete("/{menu_id}")
def delete_menu_endpoint(request: Request, menu_id: str):
    ip = request.client.host if request.client else "-"
    result = delete_menu(menu_id)
    if "error" in result:
        log_security_event(
            event_type="DELETE_MENU",
            actor="system",
            result="FAILED",
            ip=ip,
            resource=f"/api/menu/{menu_id}",
            detail=result["error"]
        )
        raise HTTPException(status_code=400, detail=result["error"])

    log_security_event(
        event_type="DELETE_MENU",
        actor="system",
        result="SUCCESS",
        ip=ip,
        resource=f"/api/menu/{menu_id}",
        detail=result.get("message", "")
    )
    return result


@router.post("/{menu_id}/activate")
def activate_menu_endpoint(request: Request, menu_id: str):
    ip = request.client.host if request.client else "-"
    result = activate_menu(menu_id)
    if "error" in result:
        log_security_event(
            event_type="ACTIVATE_MENU",
            actor="system",
            result="FAILED",
            ip=ip,
            resource=f"/api/menu/{menu_id}/activate",
            detail=result["error"]
        )
        raise HTTPException(status_code=400, detail=result["error"])

    log_security_event(
        event_type="ACTIVATE_MENU",
        actor="system",
        result="SUCCESS",
        ip=ip,
        resource=f"/api/menu/{menu_id}/activate",
        detail=result.get("message", "")
    )
    return result


@router.post("/train/{menu_name}")
def train_menu_endpoint(request: Request, menu_name: str):
    ip = request.client.host if request.client else "-"
    result = train_menu(menu_name)
    if "error" in result:
        log_security_event(
            event_type="TRAIN_MODEL",
            actor="system",
            result="FAILED",
            ip=ip,
            resource=f"/api/menu/train/{menu_name}",
            detail=result["error"]
        )
        raise HTTPException(status_code=400, detail=result["error"])

    log_security_event(
        event_type="TRAIN_MODEL",
        actor="system",
        result="SUCCESS",
        ip=ip,
        resource=f"/api/menu/train/{menu_name}",
        detail=f"Trained: {result.get('trained_cabang', 0)} cabang"
    )
    return result


@router.post("/train/all")
def train_all_menus_endpoint(request: Request):
    ip = request.client.host if request.client else "-"
    log_security_event(
        event_type="TRAIN_ALL_MODELS",
        actor="system",
        result="STARTED",
        ip=ip,
        resource="/api/menu/train/all"
    )
    result = train_all_menus()
    log_security_event(
        event_type="TRAIN_ALL_MODELS",
        actor="system",
        result="SUCCESS",
        ip=ip,
        resource="/api/menu/train/all",
        detail=result.get("message", "")
    )
    return result


@router.get("/train/status")
def get_train_status_endpoint():
    return get_train_status()
