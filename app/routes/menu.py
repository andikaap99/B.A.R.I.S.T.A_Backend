from fastapi import APIRouter, HTTPException
from app.models.schemas import MenuCreate, MenuUpdate
from app.services.menu_service import (
    get_all_menu,
    get_menu_by_id,
    create_menu,
    update_menu,
    delete_menu,
    train_menu,
    train_all_menus,
    get_train_status,
)

router = APIRouter(prefix="/api/menu", tags=["menu"])


@router.get("")
def get_all_menu_endpoint():
    data = get_all_menu()
    return {"count": len(data), "data": data}


@router.get("/{menu_id}")
def get_menu_endpoint(menu_id: str):
    data = get_menu_by_id(menu_id)
    if not data:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan")
    return {"data": data}


@router.post("")
def create_menu_endpoint(data: MenuCreate):
    result = create_menu(nama=data.nama, kategori=data.kategori, harga=data.harga)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Menu berhasil dibuat", "data": result["data"]}


@router.put("/{menu_id}")
def update_menu_endpoint(menu_id: str, data: MenuUpdate):
    result = update_menu(
        menu_id=menu_id,
        nama=data.nama,
        kategori=data.kategori,
        harga=data.harga,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Menu berhasil diupdate", "data": result["data"]}


@router.delete("/{menu_id}")
def delete_menu_endpoint(menu_id: str):
    result = delete_menu(menu_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/train/{menu_name}")
def train_menu_endpoint(menu_name: str):
    result = train_menu(menu_name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/train/all")
def train_all_menus_endpoint():
    result = train_all_menus()
    return result


@router.get("/train/status")
def get_train_status_endpoint():
    return get_train_status()
