from fastapi import APIRouter, Request
from app.models.schemas import TransaksiCreate, TransaksiResponse
from app.services.transaksi_service import (
    create_transaksi,
    get_transaksi_by_cabang,
    get_transaksi_mingguan,
)
from app.logging_config import log_security_event

router = APIRouter(prefix="/api/transaksi", tags=["transaksi"])


@router.post("", response_model=dict)
def input_transaksi(request: Request, data: TransaksiCreate):
    ip = request.client.host if request.client else "-"
    items = [{"menu": item.menu, "qty": item.qty} for item in data.items]
    result = create_transaksi(
        cabang_id=data.cabang_id,
        tanggal=data.tanggal,
        items=items,
    )

    log_security_event(
        event_type="CREATE_TRANSAKSI",
        actor=data.cabang_id,
        result="SUCCESS",
        ip=ip,
        resource="/api/transaksi",
        detail=f"{len(result)} items dari {data.cabang_id}"
    )

    return {"message": f"{len(result)} transaksi berhasil ditambahkan", "data": result}


@router.get("/{cabang_id}")
def get_transaksi(cabang_id: str):
    data = get_transaksi_by_cabang(cabang_id)
    return {"cabang_id": cabang_id, "count": len(data), "data": data}


@router.get("/mingguan/{cabang_id}")
def get_transaksi_mingguan_endpoint(cabang_id: str):
    data = get_transaksi_mingguan(cabang_id)
    return {"cabang_id": cabang_id, "periode": "7 hari terakhir", "count": len(data), "data": data}
