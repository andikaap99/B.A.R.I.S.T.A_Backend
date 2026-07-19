"""
Central logging configuration - Security Audit Trail
Dipakai di semua module (routes, services, middleware).
"""
import logging
import logging.handlers
import os
from datetime import datetime, timezone

LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)


class UTCFormatter(logging.Formatter):
    """Formatter dengan timestamp UTC eksplisit - penting untuk audit trail lintas timezone."""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.isoformat()


class SupabaseAuditHandler(logging.Handler):
    """Handler untuk mengirim security event ke tabel audit_log di Supabase."""
    def emit(self, record):
        try:
            from app.database import get_supabase
            db = get_supabase()

            log_entry = self.format(record)
            parts = {}
            for item in log_entry.split(" | ")[-1].split(" "):
                if "=" in item:
                    key, value = item.split("=", 1)
                    parts[key] = value

            db.table("audit_log").insert({
                "event_type": parts.get("event", "UNKNOWN"),
                "actor": parts.get("actor", "-"),
                "result": parts.get("result", "-"),
                "ip": parts.get("ip", "-"),
                "client_cn": parts.get("client_cn", "-"),
                "resource": parts.get("resource", "-"),
                "detail": parts.get("detail", ""),
                "method": parts.get("method", "-"),
                "path": parts.get("path", "-"),
                "status": int(parts.get("status", 0)) if parts.get("status", "").isdigit() else 0,
            }).execute()
        except Exception:
            pass


def setup_logging():
    """
    Panggil sekali di entrypoint aplikasi (main.py), sebelum app dibuat.
    Membuat 2 log terpisah:
      - app.log      -> semua log aplikasi (debug/info/error umum)
      - security.log -> khusus event keamanan (login, akses ditolak, dsb)
    """
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(message)s"
    )
    formatter = UTCFormatter(log_format)

    # Root logger -> app.log (rotasi harian, simpan 30 hari)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    app_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)

    # Tetap tampil di console/stdout (untuk docker logs / journalctl)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Logger khusus security -> security.log (rotasi harian, simpan lebih lama, misal 90 hari)
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = True  # tetap ikut masuk ke app.log & console juga

    security_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "security.log"),
        when="midnight",
        backupCount=90,
        encoding="utf-8",
    )
    security_handler.setFormatter(formatter)
    security_logger.addHandler(security_handler)

    # Supabase handler untuk audit log
    supabase_handler = SupabaseAuditHandler()
    supabase_handler.setFormatter(formatter)
    security_logger.addHandler(supabase_handler)

    return root_logger


# Logger siap pakai untuk event keamanan
security_logger = logging.getLogger("security")


def log_security_event(event_type: str, actor: str, result: str, detail: str = "", ip: str = "-", resource: str = "-", client_cn: str = "-", method: str = "-", path: str = "-", status: int = 0):
    """
    Helper standar untuk mencatat event keamanan dengan format konsisten.

    event_type: contoh "LOGIN", "ACCESS_DENIED", "DELETE_MODEL", "UPLOAD", "TOKEN_INVALID"
    actor: user_id / username / "anonymous" / CN dari client cert
    result: "SUCCESS" atau "FAILED"
    detail: keterangan tambahan bebas
    ip: IP address client
    client_cn: Common Name dari client certificate mTLS
    resource: endpoint atau resource yang diakses
    method: HTTP method (GET, POST, PUT, DELETE)
    path: URL path yang diakses
    status: HTTP status code
    """
    security_logger.info(
        f"event={event_type} actor={actor} result={result} "
        f"ip={ip} client_cn={client_cn} resource={resource} "
        f"method={method} path={path} status={status} detail={detail}"
    )
