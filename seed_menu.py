import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def create_menu_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id SERIAL PRIMARY KEY,
            nama TEXT UNIQUE NOT NULL,
            harga INTEGER NOT NULL
        )
    """)
    conn.commit()
    print("[OK] Tabel menu berhasil dibuat/dicek")
    cur.close()
    conn.close()


def seed_menu():
    conn = get_conn()
    cur = conn.cursor()
    menus = [
        ("Chocolate Croissant", 46900),
        ("Ginger Scone", 26500),
        ("Cranberry Scone", 40600),
        ("Latte", 37500),
        ("Columbian Medium Roast Rg", 25000),
        ("Latte Rg", 42500),
        ("Dark chocolate Lg", 45000),
        ("Sustainably Grown Organic Lg", 47500),
        ("Sustainably Grown Organic Rg", 37500),
        ("Earl Grey Rg", 25000),
        ("Morning Sunrise Chai Rg", 25000),
        ("Peppermint Rg", 25000),
    ]
    cur.executemany(
        "INSERT INTO menu (nama, harga) VALUES (%s, %s) ON CONFLICT (nama) DO NOTHING",
        menus,
    )
    conn.commit()
    print(f"[OK] {cur.rowcount} menu berhasil di-insert")
    cur.close()
    conn.close()


if __name__ == "__main__":
    print("=== Seeding Menu ke Supabase ===\n")
    create_menu_table()
    seed_menu()
    print("\n=== Selesai ===")
