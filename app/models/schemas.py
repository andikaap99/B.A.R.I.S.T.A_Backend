from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional


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
    keterangan: bool
    tanggal: date
    created_at: datetime


class PrediksiItem(BaseModel):
    menu: str
    prediksi_qty: float
    tanggal: str


class PrediksiResponse(BaseModel):
    cabang_id: str
    periode_minggu: str
    generated_at: str
    prediksi: List[PrediksiItem]


class PromoItem(BaseModel):
    hari: str
    tanggal: str
    menu: str
    kuadran: str
    harga_normal: float
    diskon: str
    harga_promo: float
    alasan: str


class PromoResponse(BaseModel):
    cabang_id: str
    periode_minggu: str
    generated_at: str
    rekomendasi_promo: List[PromoItem]


class MenuEngineeringResponse(BaseModel):
    star: List[str]
    plowhorse: List[str]
    puzzle: List[str]
    dog: List[str]


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


class MenuCreate(BaseModel):
    nama: str
    kategori: str
    harga: float


class MenuUpdate(BaseModel):
    nama: Optional[str] = None
    kategori: Optional[str] = None
    harga: Optional[float] = None


class MenuResponse(BaseModel):
    id: str
    nama: str
    kategori: str
    harga: float
    is_active: bool
    created_at: datetime


class TrainStatusItem(BaseModel):
    menu: str
    has_model: bool


class TrainStatusResponse(BaseModel):
    total_menu: int
    trained: int
    untrained: int
    menus: List[TrainStatusItem]


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
