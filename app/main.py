from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import transaksi, hasil_dss, dashboard, auth, cabang, menu, promo
from app.scheduler import start_scheduler, trigger_dss_engine, get_scheduler_status
from app.database import get_supabase
from app.storage import get_minio_client

app = FastAPI(title="DSS Multi-Cabang Coffee Shop Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaksi.router)
app.include_router(hasil_dss.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(cabang.router)
app.include_router(menu.router)
app.include_router(promo.router)


@app.on_event("startup")
def startup():
    start_scheduler()


@app.get("/")
def health_check():
    return {"status": "ok", "service": "DSS Backend Coffee Shop"}


@app.get("/api/health")
def check_connections():
    status = {"supabase": "error", "minio": "error"}

    try:
        db = get_supabase()
        db.table("cabang").select("id").limit(1).execute()
        status["supabase"] = "connected"
    except Exception as e:
        status["supabase"] = f"error: {str(e)}"

    try:
        client = get_minio_client()
        client.list_buckets()
        status["minio"] = "connected"
    except Exception as e:
        status["minio"] = f"error: {str(e)}"

    return {"status": status}


@app.post("/api/scheduler/trigger")
def trigger_dss():
    trigger_dss_engine()
    return {"message": "DSS Engine triggered successfully"}


@app.get("/api/scheduler/status")
def scheduler_status():
    return get_scheduler_status()
