from pydantic import BaseModel
from datetime import date, datetime
from typing import List


class TransaksiItem(BaseModel):
    menu: str
    qty: int


class TransaksiCreate(BaseModel):
    cabang_id: str
    tanggal: date
    items: list[TransaksiItem]


class TransaksiResponse(BaseModel):
    id: str
    cabang_id: str
    menu: str
    qty: int
    harga: float
    tanggal: date
    created_at: datetime


class PrediksiItem(BaseModel):
    menu: str
    prediksi_qty: float
    tanggal: date


class PrediksiResponse(BaseModel):
    cabang_id: str
    periode_minggu: date
    prediksi: List[PrediksiItem]


class PromoItem(BaseModel):
    menu: str
    alasan: str
    hari: str
    tanggal: date


class PromoResponse(BaseModel):
    cabang_id: str
    periode_minggu: date
    rekomendasi_promo: List[PromoItem]


class DashboardCabang(BaseModel):
    cabang_id: str
    nama: str
    total_revenue: float
    total_transaksi: int
    top_menu: str


class PerbandinganCabang(BaseModel):
    cabang_id: str
    nama: str
    revenue_mingguan: float
    transaksi_mingguan: int
    menu_terlaris: str


class CabangCreate(BaseModel):
    id: str
    nama: str
    lokasi: str


class CabangResponse(BaseModel):
    id: str
    nama: str
    lokasi: str


class UserCreate(BaseModel):
    username: str
    password: str
    cabang_id: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    cabang_id: str | None = None
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
