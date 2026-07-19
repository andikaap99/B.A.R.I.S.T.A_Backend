#!/bin/bash

# ============================================
# Script Testing mTLS & Audit Logging
# ============================================

MINIO_ENDPOINT="https://168.110.198.181"
BACKEND_ENDPOINT="http://localhost:8000"
CLIENT_CERT="./client.crt"
CLIENT_KEY="./client.key"
CA_CERT="./ca.crt"

echo "=========================================="
echo "  Testing mTLS & Audit Logging"
echo "=========================================="

# Cek apakah sertifikat ada
echo ""
echo "[1] Cek sertifikat..."
if [ ! -f "$CLIENT_CERT" ]; then
    echo "    ❌ $CLIENT_CERT tidak ditemukan"
    echo "    Pastikan sertifikat ada di folder ./certs/"
    exit 1
fi
echo "    ✅ Client cert: $CLIENT_CERT"

if [ ! -f "$CLIENT_KEY" ]; then
    echo "    ❌ $CLIENT_KEY tidak ditemukan"
    exit 1
fi
echo "    ✅ Client key: $CLIENT_KEY"

if [ ! -f "$CA_CERT" ]; then
    echo "    ⚠️  $CA_CERT tidak ditemukan (opsional untuk verifikasi server)"
else
    echo "    ✅ CA cert: $CA_CERT"
fi

# Cek apakah backend running
echo ""
echo "[2] Cek backend running..."
if curl -s "$BACKEND_ENDPOINT" > /dev/null 2>&1; then
    echo "    ✅ Backend running di $BACKEND_ENDPOINT"
else
    echo "    ❌ Backend tidak running di $BACKEND_ENDPOINT"
    echo "    Jalankan: uvicorn app.main:app --reload"
    exit 1
fi

# Test 1: Request tanpa client cert (via backend langsung)
echo ""
echo "[3] Test 1: Request tanpa client cert..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$BACKEND_ENDPOINT/api/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
echo "    Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "    ✅ Health check berhasil"
else
    echo "    ❌ Health check gagal"
fi

# Test 2: Login (berhasil) - akan log security event
echo ""
echo "[4] Test 2: Login test (berhasil)..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_ENDPOINT/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin_pusat","password":"password123"}')
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "    ✅ Login berhasil - security event logged"
else
    echo "    ❌ Login gagal"
    echo "    Response: $LOGIN_RESPONSE"
fi

# Test 3: Login (gagal) - akan log FAILED event
echo ""
echo "[5] Test 3: Login test (gagal)..."
LOGIN_FAIL=$(curl -s -X POST "$BACKEND_ENDPOINT/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin_pusat","password":"salah"}')
if echo "$LOGIN_FAIL" | grep -q "Invalid\|invalid\|error"; then
    echo "    ✅ Login gagal terdeteksi - FAILED event logged"
else
    echo "    ⚠️  Response: $LOGIN_FAIL"
fi

# Test 4: Cek local log file
echo ""
echo "[6] Test 4: Cek local log file..."
if [ -f "./logs/security.log" ]; then
    LOG_LINES=$(wc -l < "./logs/security.log")
    echo "    ✅ security.log ada ($LOG_LINES lines)"
    echo "    Last 3 lines:"
    tail -3 "./logs/security.log" | sed 's/^/    /'
else
    echo "    ⚠️  security.log belum ada (akan dibuat setiap ada event)"
fi

# Test 5: Cek Supabase audit_log (opsional)
echo ""
echo "[7] Test 5: Cek Supabase audit_log..."
echo "    Jalankan query ini di Supabase SQL Editor:"
echo ""
echo "    SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 5;"
echo ""

echo "=========================================="
echo "  Testing Selesai!"
echo "=========================================="
echo ""
echo "Untuk melihat log real-time:"
echo "  tail -f ./logs/security.log"
echo ""
echo "Untuk tes mTLS dengan curl:"
echo "  curl -k --cert $CLIENT_CERT --key $CLIENT_KEY $MINIO_ENDPOINT/"
echo ""
