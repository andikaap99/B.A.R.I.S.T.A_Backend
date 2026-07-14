# API Documentation — DSS Backend

**Base URL:** `http://localhost:8000`

Semua endpoint mengembalikan JSON. Gunakan header `Content-Type: application/json`.

---

## Autentikasi

### POST /api/auth/register
Register user baru.

**Request:**
```json
{
  "username": "kasir_astoria",
  "password": "password123",
  "cabang_id": "cabang_1"    // nullable, null = role pusat
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "kasir_astoria",
    "cabang_id": "cabang_1",
    "role": "cabang",
    "created_at": "2026-07-13T05:00:00"
  }
}
```

---

### POST /api/auth/login
Login user.

**Request:**
```json
{
  "username": "kasir_astoria",
  "password": "password123"
}
```

**Response (200):** Sama seperti register.

---

## Cabang

### POST /api/cabang
Tambah data cabang baru.

**Request:**
```json
{
  "id": "cabang_4",
  "nama": "Cabang Brooklyn",
  "lokasi": "Brooklyn"
}
```

**Response (200):**
```json
{
  "message": "Cabang berhasil dibuat",
  "data": {
    "id": "cabang_4",
    "nama": "Cabang Brooklyn",
    "lokasi": "Brooklyn"
  }
}
```

**Error (400):**
```json
{ "error": "Cabang dengan id 'cabang_4' sudah ada" }
```

---

### GET /api/cabang
Ambil semua data cabang.

**Response (200):**
```json
{
  "data": [
    { "id": "cabang_1", "nama": "Cabang Astoria", "lokasi": "Astoria" },
    { "id": "cabang_2", "nama": "Cabang Hell Kitchen", "lokasi": "Hell Kitchen" },
    { "id": "cabang_3", "nama": "Cabang Lower Manhattan", "lokasi": "Lower Manhattan" }
  ]
}
```

---

### GET /api/cabang/{cabang_id}
Ambil data satu cabang.

**Response (200):**
```json
{
  "data": {
    "id": "cabang_1",
    "nama": "Cabang Astoria",
    "lokasi": "Astoria"
  }
}
```

**Error (400):**
```json
{ "error": "Cabang tidak ditemukan" }
```

---

## Menu

### GET /api/menu
Ambil semua menu yang aktif.

**Response (200):**
```json
{
  "count": 12,
  "data": [
    {
      "id": "uuid",
      "nama": "Chocolate Croissant",
      "kategori": "Bakery",
      "harga": 46900,
      "is_active": true,
      "created_at": "2026-07-13T05:00:00"
    }
  ]
}
```

---

### GET /api/menu/inactive
Ambil semua menu yang sudah non-aktif (soft delete).

**Response (200):**
```json
{
  "count": 2,
  "data": [
    {
      "id": "uuid",
      "nama": "Mocha",
      "kategori": "Coffee",
      "harga": 45000,
      "is_active": false,
      "created_at": "2026-07-13T05:00:00"
    }
  ]
}
```

---

### GET /api/menu/{id}
Ambil detail satu menu.

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "nama": "Chocolate Croissant",
    "kategori": "Bakery",
    "harga": 46900,
    "is_active": true,
    "created_at": "2026-07-13T05:00:00"
  }
}
```

**Error (404):**
```json
{ "detail": "Menu tidak ditemukan" }
```

---

### POST /api/menu
Tambah menu baru.

**Request:**
```json
{
  "nama": "Mocha",
  "kategori": "Coffee",
  "harga": 45000
}
```

**Response (200):**
```json
{
  "message": "Menu berhasil dibuat",
  "data": {
    "id": "uuid",
    "nama": "Mocha",
    "kategori": "Coffee",
    "harga": 45000,
    "is_active": true,
    "created_at": "2026-07-13T05:00:00"
  }
}
```

**Error (400):**
```json
{ "detail": "Menu 'Mocha' sudah ada" }
```

---

### PUT /api/menu/{id}
Edit menu. Jika nama berubah, model.pkl akan diupdate otomatis.

**Request:**
```json
{
  "nama": "Mocha Baru",
  "kategori": "Coffee",
  "harga": 50000
}
```

**Response (200):**
```json
{
  "message": "Menu berhasil diupdate",
  "data": { ... }
}
```

---

### DELETE /api/menu/{id}
Soft delete menu (set `is_active=false`). Model.pkl juga akan diupdate.

**Response (200):**
```json
{ "message": "Menu 'Mocha' berhasil dihapus (soft delete)" }
```

---

### POST /api/menu/{id}/activate
Aktifkan kembali menu yang sudah non-aktif.

**Response (200):**
```json
{ "message": "Menu 'Mocha' berhasil diaktifkan kembali" }
```

**Error (400):**
```json
{ "detail": "Menu 'Mocha' sudah aktif" }
```

---

### POST /api/menu/train/{menu_name}
Train model untuk 1 menu (3 cabang). Minimal 7 hari data transaksi.

**Response (200):**
```json
{
  "message": "Berhasil train menu 'Latte'",
  "trained_cabang": 3,
  "total_models_in_pkl": 36
}
```

**Error (400):**
```json
{ "detail": "Tidak ada data transaksi untuk menu 'Latte'" }
```

---

### POST /api/menu/train/all
Retrain semua model (36 model = 12 menu x 3 cabang).

**Response (200):**
```json
{
  "message": "Training selesai: 12 sukses, 0 gagal",
  "results": [ ... ]
}
```

---

### GET /api/menu/train/status
Cek status training semua menu.

**Response (200):**
```json
{
  "total_menu": 12,
  "trained": 10,
  "untrained": 2,
  "menus": [
    { "menu": "Latte", "has_model": true },
    { "menu": "Mocha", "has_model": false }
  ]
}
```

---

## Transaksi

### POST /api/transaksi
Input transaksi baru dari cabang (bisa beberapa item sekaligus). Harga otomatis diambil dari tabel `menu`. Jika menu memiliki promo aktif, harga otomatis diskon dan `keterangan = true`.

**Request:**
```json
{
  "cabang_id": "cabang_1",
  "tanggal": "2026-07-13",
  "items": [
    { "menu": "Latte", "qty": 5 },
    { "menu": "Cranberry Scone", "qty": 3 }
  ]
}
```

**Response (200):**
```json
{
  "message": "2 transaksi berhasil ditambahkan",
  "data": [
    {
      "id": "uuid",
      "cabang_id": "cabang_1",
      "menu": "Latte",
      "qty": 5,
      "harga": 37500,
      "keterangan": false,
      "tanggal": "2026-07-13",
      "created_at": "..."
    },
    {
      "id": "uuid",
      "cabang_id": "cabang_1",
      "menu": "Cranberry Scone",
      "qty": 3,
      "harga": 32480,
      "keterangan": true,
      "tanggal": "2026-07-13",
      "created_at": "..."
    }
  ]
}
```

> **Catatan:** `keterangan = true` berarti transaksi menggunakan promo (harga diskon). `keterangan = false` berarti harga normal.

---

### GET /api/transaksi/{cabang_id}
Ambil semua transaksi suatu cabang.

**Response (200):**
```json
{
  "cabang_id": "cabang_1",
  "count": 84,
  "data": [
    {
      "id": "uuid",
      "cabang_id": "cabang_1",
      "menu": "Latte",
      "qty": 5,
      "harga": 45000,
      "keterangan": false,
      "tanggal": "2026-07-13",
      "created_at": "..."
    }
  ]
}
```

---

### GET /api/transaksi/mingguan/{cabang_id}
Ambil transaksi 7 hari terakhir suatu cabang.

**Response (200):** Sama seperti `GET /api/transaksi/{cabang_id}`, hanya data terbatas 7 hari.

---

## Struktur Database

### Tabel `menu` (sudah di-ALTER)
```sql
CREATE TABLE menu (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nama VARCHAR NOT NULL UNIQUE,
  kategori VARCHAR NOT NULL,
  harga NUMERIC(10,2),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now()
);
```

### Tabel `promo` (baru)
```sql
CREATE TABLE promo (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  cabang_id VARCHAR NOT NULL,
  menu_nama VARCHAR NOT NULL,
  kuadran VARCHAR NOT NULL,
  harga_normal NUMERIC(10,2),
  diskon VARCHAR NOT NULL,
  harga_promo NUMERIC(10,2),
  kuota INT DEFAULT 20,
  terpakai INT DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  periode_minggu DATE NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);
```

> **Catatan:** 
> - `kuota` = batas maksimal promo dipakai per hari (default: 20)
> - `terpakai` = jumlah promo yang sudah dipakai hari ini
> - Kuota direset otomatis setiap jam 00:00 WIB

### Tabel `transaksi` (update)
```sql
ALTER TABLE transaksi ADD COLUMN keterangan BOOLEAN DEFAULT false;
```

> **Catatan:** `keterangan = true` berarti transaksi menggunakan promo.

---

## Hasil DSS

### GET /api/hasil-dss/{cabang_id}
Ambil hasil DSS terbaru (prediksi + rekomendasi promo + menu engineering) untuk satu cabang.

**Response (200):**
```json
{
  "cabang_id": "cabang_1",
  "hasil": {
    "prediksi": {
      "cabang_id": "cabang_1",
      "periode_minggu": "2026-07-13",
      "generated_at": "2026-07-13T23:00:00",
      "prediksi": [
        { "menu": "Latte", "prediksi_qty": 12.67, "tanggal": "2026-07-14" }
      ]
    },
    "rekomendasi_promo": {
      "cabang_id": "cabang_1",
      "periode_minggu": "2026-07-13",
      "generated_at": "2026-07-13T23:00:00",
      "rekomendasi_promo": [
        {
          "hari": "Senin",
          "tanggal": "2026-07-14",
          "menu": "Cranberry Scone",
          "kuadran": "Dog",
          "harga_normal": 40600,
          "diskon": "20%",
          "harga_promo": 32480,
          "alasan": "Prediksi penjualan rendah, margin rendah"
        }
      ]
    },
    "menu_engineering": {
      "star": ["Latte", "Earl Grey Rg"],
      "plowhorse": ["Latte Rg"],
      "puzzle": ["Dark chocolate Lg"],
      "dog": ["Cranberry Scone"]
    }
  }
}
```

**Error (404):**
```json
{ "detail": "Belum ada hasil DSS untuk cabang ini" }
```

---

### GET /api/hasil-dss/prediksi/{cabang_id}
Ambil hanya prediksi penjualan untuk satu cabang.

**Response (200):**
```json
{
  "cabang_id": "cabang_1",
  "periode_minggu": "2026-07-13",
  "generated_at": "2026-07-13T23:00:00",
  "prediksi": [
    { "menu": "Latte", "prediksi_qty": 12.67, "tanggal": "2026-07-14" },
    { "menu": "Espresso", "prediksi_qty": 25.71, "tanggal": "2026-07-14" }
  ]
}
```

---

### GET /api/hasil-dss/promo/{cabang_id}
Ambil hanya rekomendasi promo untuk satu cabang.

**Response (200):**
```json
{
  "cabang_id": "cabang_1",
  "periode_minggu": "2026-07-13",
  "generated_at": "2026-07-13T23:00:00",
  "rekomendasi_promo": [
    {
      "hari": "Senin",
      "tanggal": "2026-07-14",
      "menu": "Cranberry Scone",
      "kuadran": "Dog",
      "harga_normal": 40600,
      "diskon": "20%",
      "harga_promo": 32480,
      "alasan": "Prediksi penjualan rendah, margin rendah"
    }
  ]
}
```

---

### GET /api/hasil-dss/engineering/{cabang_id}
Ambil menu engineering matrix untuk satu cabang.

**Response (200):**
```json
{
  "cabang_id": "cabang_1",
  "periode_minggu": "2026-07-13",
  "generated_at": "2026-07-13T23:00:00",
  "menu_engineering": {
    "star": ["Latte", "Earl Grey Rg"],
    "plowhorse": ["Latte Rg"],
    "puzzle": ["Dark chocolate Lg"],
    "dog": ["Cranberry Scone"]
  }
}
```

---

## Dashboard Pusat

### GET /api/dashboard/semua-cabang
Ringkasan semua cabang: total revenue, jumlah transaksi, top menu (7 hari terakhir).

**Response (200):**
```json
{
  "periode": "7 hari terakhir",
  "data": [
    {
      "cabang_id": "cabang_1",
      "nama": "Cabang Astoria",
      "total_revenue": 15750000,
      "total_transaksi": 84,
      "top_menu": "Latte"
    }
  ]
}
```

---

### GET /api/dashboard/perbandingan
Perbandingan performa antar cabang.

**Response (200):**
```json
{
  "periode": "7 hari terakhir",
  "data": [
    {
      "cabang_id": "cabang_1",
      "nama": "Cabang Astoria",
      "revenue_mingguan": 15750000,
      "transaksi_mingguan": 84,
      "menu_terlaris": "Latte"
    }
  ]
}
```

---

### GET /api/dashboard/hasil-dss-global
Hasil DSS semua cabang sekaligus (prediksi + promo + engineering per cabang).

**Response (200):**
```json
{
  "data": [
    {
      "cabang_id": "cabang_1",
      "nama": "Cabang Astoria",
      "hasil_dss": {
        "prediksi": { ... },
        "rekomendasi_promo": { ... },
        "menu_engineering": { ... }
      }
    }
  ]
}
```

---

## Scheduler

### POST /api/scheduler/trigger
Trigger DSS Engine manual (untuk testing). Proses berjalan di background.

**Response (200):**
```json
{ "message": "DSS Engine triggered successfully" }
```

---

### GET /api/scheduler/status
Cek status scheduler.

**Response (200):**
```json
{
  "running": true,
  "jobs": [
    {
      "id": "dss_engine_weekly",
      "next_run_time": "2026-07-19 23:00:00+07:00"
    }
  ]
}
```

---

## Health Check

### GET /
```json
{ "status": "ok", "service": "DSS Backend Coffee Shop" }
```

### GET /api/health
```json
{
  "status": {
    "supabase": "connected",
    "minio": "connected"
  }
}
```

---

## Promo

### GET /api/promo/{cabang_id}
Ambil semua promo aktif untuk suatu cabang.

**Response (200):**
```json
{
  "cabang_id": "cabang_1",
  "count": 3,
  "data": [
    {
      "id": "uuid",
      "cabang_id": "cabang_1",
      "menu_nama": "Cranberry Scone",
      "kuadran": "Dog",
      "harga_normal": 40600,
      "diskon": "20%",
      "harga_promo": 32480,
      "kuota": 20,
      "terpakai": 5,
      "sisa_kuota": 15,
      "is_active": true,
      "periode_minggu": "2026-07-13",
      "created_at": "2026-07-13T23:00:00"
    }
  ]
}
```

> **Catatan:** 
> - `sisa_kuota` = `kuota - terpakai`
> - Jika `sisa_kuota = 0`, promo tidak akan diterapkan di transaksi baru
> - Kuota direset otomatis setiap jam 00:00 WIB

---

## Menu Engineering Matrix

| Kuadran | Popularitas | Profitabilitas | Strategi |
|---------|-------------|----------------|----------|
| ⭐ Star | Tinggi | Tinggi | Pertahankan, jangan promo |
| 🐄 Plowhorse | Tinggi | Rendah | Coba tingkatkan harga |
| ❓ Puzzle | Rendah | Tinggi | Promo 10% |
| 🐕 Dog | Rendah | Rendah | Promo 20-25% |

---

## Menu yang Digunakan
12 menu hasil training model:
| No | Menu | Kategori |
|----|------|----------|
| 1 | Chocolate Croissant | Bakery |
| 2 | Ginger Scone | Bakery |
| 3 | Cranberry Scone | Bakery |
| 4 | Latte | Coffee |
| 5 | Columbian Medium Roast Rg | Coffee |
| 6 | Latte Rg | Coffee |
| 7 | Dark chocolate Lg | Drinking Chocolate |
| 8 | Sustainably Grown Organic Lg | Coffee |
| 9 | Sustainably Grown Organic Rg | Coffee |
| 10 | Earl Grey Rg | Tea |
| 11 | Morning Sunrise Chai Rg | Tea |
| 12 | Peppermint Rg | Tea |

---

## Data Dummy Users
| Username | Password | Role | Cabang |
|----------|----------|------|--------|
| admin_pusat | password123 | pusat | - |
| kasir_astoria | password123 | cabang | cabang_1 |
| kasir_hell | password123 | cabang | cabang_2 |
| kasir_manhattan | password123 | cabang | cabang_3 |
