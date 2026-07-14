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

## Transaksi

### POST /api/transaksi
Input transaksi baru dari cabang (bisa beberapa item sekaligus).

**Request:**
```json
{
  "cabang_id": "cabang_1",
  "tanggal": "2026-07-13",
  "items": [
    { "menu": "Latte", "qty": 5, "harga": 45000 },
    { "menu": "Espresso", "qty": 3, "harga": 35000 }
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
      "harga": 45000,
      "tanggal": "2026-07-13",
      "created_at": "..."
    },
    {
      "id": "uuid",
      "cabang_id": "cabang_1",
      "menu": "Espresso",
      "qty": 3,
      "harga": 35000,
      "tanggal": "2026-07-13",
      "created_at": "..."
    }
  ]
}
```

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

## Hasil DSS

### GET /api/hasil-dss/{cabang_id}
Ambil hasil DSS terbaru (prediksi + rekomendasi promo) untuk satu cabang.

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
        { "menu": "Latte", "prediksi_qty": 12.67, "tanggal": "2026-07-14" },
        { "menu": "Latte", "prediksi_qty": 12.73, "tanggal": "2026-07-15" }
      ]
    },
    "rekomendasi_promo": {
      "cabang_id": "cabang_1",
      "periode_minggu": "2026-07-13",
      "generated_at": "2026-07-13T23:00:00",
      "rekomendasi_promo": [
        { "hari": "Senin", "tanggal": "2026-07-14", "menu": "Mocha", "alasan": "prediksi penjualan terendah" }
      ]
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
    { "hari": "Senin", "tanggal": "2026-07-14", "menu": "Mocha", "alasan": "prediksi penjualan terendah" },
    { "hari": "Selasa", "tanggal": "2026-07-15", "menu": "Latte", "alasan": "prediksi penjualan terendah" }
  ]
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
Hasil DSS semua cabang sekaligus (prediksi + promo per cabang).

**Response (200):**
```json
{
  "data": [
    {
      "cabang_id": "cabang_1",
      "nama": "Cabang Astoria",
      "hasil_dss": {
        "prediksi": { ... },
        "rekomendasi_promo": { ... }
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

## Menu yang Digunakan
12 menu hasil training model:
| No | Menu |
|----|------|
| 1 | Chocolate Croissant |
| 2 | Ginger Scone |
| 3 | Cranberry Scone |
| 4 | Latte |
| 5 | Columbian Medium Roast Rg |
| 6 | Latte Rg |
| 7 | Dark chocolate Lg |
| 8 | Sustainably Grown Organic Lg |
| 9 | Sustainably Grown Organic Rg |
| 10 | Earl Grey Rg |
| 11 | Morning Sunrise Chai Rg |
| 12 | Peppermint Rg |

---

## Data Dummy Users
| Username | Password | Role | Cabang |
|----------|----------|------|--------|
| admin_pusat | password123 | pusat | - |
| kasir_astoria | password123 | cabang | cabang_1 |
| kasir_hell | password123 | cabang | cabang_2 |
| kasir_manhattan | password123 | cabang | cabang_3 |
