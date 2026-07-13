from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from app.database import get_supabase
from app.config import SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register_user(username: str, password: str, cabang_id: str | None = None):
    db = get_supabase()

    existing = db.table("users").select("*").eq("username", username).execute()
    if existing.data:
        return {"error": "Username sudah digunakan"}

    hashed = hash_password(password)
    result = db.table("users").insert({
        "username": username,
        "password": hashed,
        "cabang_id": cabang_id,
        "role": "pusat" if cabang_id is None else "cabang",
    }).execute()

    user = result.data[0]
    token = create_access_token({"sub": user["id"], "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "cabang_id": user.get("cabang_id"),
            "role": user["role"],
            "created_at": user["created_at"],
        },
    }


def login_user(username: str, password: str):
    db = get_supabase()

    result = db.table("users").select("*").eq("username", username).execute()
    if not result.data:
        return {"error": "Username atau password salah"}

    user = result.data[0]
    if not verify_password(password, user["password"]):
        return {"error": "Username atau password salah"}

    token = create_access_token({"sub": user["id"], "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "cabang_id": user.get("cabang_id"),
            "role": user["role"],
            "created_at": user["created_at"],
        },
    }
