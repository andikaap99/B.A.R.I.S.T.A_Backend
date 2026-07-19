"""
Middleware audit trail - mencatat SETIAP request masuk ke API.
Pasang di main.py: app.add_middleware(AuditLoggingMiddleware)
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("security")


def extract_cn(dn_string: str) -> str:
    """
    Extract CN (Common Name) dari full DN string.
    Contoh input: CN=backend-fastapi-client,O=DSS-MinIO-KBD,C=ID
    Contoh output: backend-fastapi-client
    """
    for part in dn_string.split(","):
        if part.strip().startswith("CN="):
            return part.strip()[3:]
    return dn_string


def get_client_cert_cn(request: Request) -> str:
    """
    Ambil Common Name (CN) dari client certificate mTLS, kalau ada.
    NGINX perlu diset untuk forward info cert via header, misal:
        proxy_set_header X-Client-Cert-CN $ssl_client_s_dn;
    """
    dn = request.headers.get("X-Client-Cert-CN")
    if not dn:
        return "no-cert"
    return extract_cn(dn)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        client_ip = request.client.host if request.client else "-"
        # Kalau di belakang NGINX, IP asli ada di header ini (sudah kalian set di config NGINX)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        client_cn = get_client_cert_cn(request)
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            status = response.status_code
            level = logging.INFO if status < 400 else logging.WARNING

            logger.log(
                level,
                f"event=HTTP_REQUEST method={method} path={path} "
                f"status={status} ip={client_ip} client_cn={client_cn} "
                f"duration_ms={duration_ms}"
            )
            return response

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"event=HTTP_REQUEST_ERROR method={method} path={path} "
                f"ip={client_ip} client_cn={client_cn} "
                f"duration_ms={duration_ms} error={str(e)}"
            )
            raise
