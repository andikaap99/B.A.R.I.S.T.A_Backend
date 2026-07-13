import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
import psycopg2
import bcrypt

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def seed_cabang():
    conn = get_conn()
    cur = conn.cursor()
    cabang_list = [
        ("cabang_1", "Cabang Astoria", "Astoria"),
        ("cabang_2", "Cabang Hell Kitchen", "Hell Kitchen"),
        ("cabang_3", "Cabang Lower Manhattan", "Lower Manhattan"),
    ]
    cur.executemany(
        "INSERT INTO cabang (id, nama, lokasi) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
        cabang_list,
    )
    conn.commit()
    print(f"[OK] {cur.rowcount} cabang berhasil di-insert")
    cur.close()
    conn.close()


def seed_users():
    conn = get_conn()
    cur = conn.cursor()
    password = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
    users = [
        ("admin_pusat", password, None, "pusat"),
        ("kasir_astoria", password, "cabang_1", "cabang"),
        ("kasir_hell", password, "cabang_2", "cabang"),
        ("kasir_manhattan", password, "cabang_3", "cabang"),
    ]
    cur.executemany(
        "INSERT INTO users (username, password, cabang_id, role) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
        users,
    )
    conn.commit()
    print(f"[OK] {cur.rowcount} users berhasil di-insert (password: password123)")
    cur.close()
    conn.close()


def seed_transaksi():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM transaksi")
    print(f"[OK] {cur.rowcount} transaksi lama dihapus")

    menus = [
        "Chocolate Croissant", "Ginger Scone", "Cranberry Scone",
        "Latte", "Columbian Medium Roast Rg", "Latte Rg",
        "Dark chocolate Lg", "Sustainably Grown Organic Lg", "Sustainably Grown Organic Rg",
        "Earl Grey Rg", "Morning Sunrise Chai Rg", "Peppermint Rg",
    ]
    cabang_ids = ["cabang_1", "cabang_2", "cabang_3"]

    transaksi_list = []
    today = date.today()

    for i in range(7):
        tanggal = today - timedelta(days=6 - i)
        for cabang_id in cabang_ids:
            for menu in menus:
                qty = random.randint(3, 25)
                harga = random.choice([35000, 40000, 42000, 45000, 48000, 50000, 55000])
                transaksi_list.append((cabang_id, menu, qty, harga, tanggal))

    cur.executemany(
        "INSERT INTO transaksi (cabang_id, menu, qty, harga, tanggal) VALUES (%s, %s, %s, %s, %s)",
        transaksi_list,
    )
    conn.commit()
    print(f"[OK] {cur.rowcount} transaksi baru berhasil di-insert (7 hari x 3 cabang x {len(menus)} menu)")
    cur.close()
    conn.close()


if __name__ == "__main__":
    print("=== Seeding Data ke Supabase (via psycopg2) ===\n")
    seed_cabang()
    seed_users()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM hasil_dss")
    print(f"[OK] {cur.rowcount} hasil_dss lama dihapus")
    conn.commit()
    cur.close()
    conn.close()
    seed_transaksi()
    print("\n=== Selesai ===")
