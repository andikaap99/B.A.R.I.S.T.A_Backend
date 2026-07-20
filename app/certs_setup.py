"""
Certificates Setup - Generate mTLS certs from environment variables.

Reads CLIENT_CERT, CLIENT_KEY, CA_CERT from env vars (PEM strings with
literal \\n), writes them to certs/ folder as physical files for boto3 mTLS.
Idempotent: safe to call on every restart.
"""
import os

CERTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "certs")
CLIENT_CERT_PATH = os.path.join(CERTS_DIR, "client.crt")
CLIENT_KEY_PATH = os.path.join(CERTS_DIR, "client.key")
CA_CERT_PATH = os.path.join(CERTS_DIR, "ca.crt")

_ENV_KEYS = {
    "CLIENT_CERT": CLIENT_CERT_PATH,
    "CLIENT_KEY": CLIENT_KEY_PATH,
    "CA_CERT": CA_CERT_PATH,
}


def _convert_pem(raw: str) -> str:
    return raw.replace("\\n", "\n").strip() + "\n"


def _read_file(path: str) -> str | None:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


def _write_file(path: str, content: str) -> None:
    os.makedirs(CERTS_DIR, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def ensure_certs() -> None:
    """Generate certificate files from env vars if not already present or changed.

    Raises EnvironmentError if any required env var is not set.
    """
    missing = [k for k in _ENV_KEYS if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Environment variable(s) {', '.join(missing)} not set. "
            f"Please set them in Railway dashboard with PEM content (use \\n for newlines)."
        )

    for env_key, file_path in _ENV_KEYS.items():
        raw = os.getenv(env_key, "")
        pem_content = _convert_pem(raw)
        existing = _read_file(file_path)
        if existing != pem_content:
            _write_file(file_path, pem_content)


def get_cert_paths() -> dict:
    """Return paths to generated certificate files."""
    return {
        "cert_file": CLIENT_CERT_PATH,
        "key_file": CLIENT_KEY_PATH,
        "ca_file": CA_CERT_PATH,
    }
