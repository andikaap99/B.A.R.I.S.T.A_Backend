import httpx
from urllib.parse import quote
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import get_session as get_boto_session
from app.config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from app.certs_setup import ensure_certs, get_cert_paths

AWS_REGION = "us-east-1"
SERVICE_NAME = "s3"


def _get_boto_credentials():
    session = get_boto_session()
    session.set_credentials(MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
    return session.get_credentials()


def _sign_request(method: str, url: str, headers: dict | None = None, body: bytes = b"") -> dict:
    creds = _get_boto_credentials()
    request = AWSRequest(method=method, url=url, headers=headers or {}, data=body)
    SigV4Auth(creds, SERVICE_NAME, AWS_REGION).add_auth(request)
    return dict(request.headers)


def get_httpx_client():
    ensure_certs()
    certs = get_cert_paths()
    return httpx.Client(
        base_url=f"https://{MINIO_ENDPOINT}",
        cert=(certs["cert_file"], certs["key_file"]),
        verify=False,
        timeout=30.0,
    )


def s3_list_buckets() -> list[str]:
    client = get_httpx_client()
    url = f"https://{MINIO_ENDPOINT}/"
    headers = _sign_request("GET", url)
    resp = client.get("/", headers=headers)
    resp.raise_for_status()
    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.text)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    return [b.find("s3:Name", ns).text for b in root.findall(".//s3:Bucket", ns)]


def s3_put_object(bucket: str, key: str, body: bytes, content_type: str = "application/octet-stream"):
    client = get_httpx_client()
    url = f"https://{MINIO_ENDPOINT}/{quote(bucket)}/{quote(key)}"
    headers = _sign_request("PUT", url, {"Content-Type": content_type}, body)
    headers["Content-Type"] = content_type
    resp = client.put(f"/{bucket}/{key}", content=body, headers=headers)
    resp.raise_for_status()


def s3_get_object(bucket: str, key: str) -> bytes:
    client = get_httpx_client()
    url = f"https://{MINIO_ENDPOINT}/{quote(bucket)}/{quote(key)}"
    headers = _sign_request("GET", url)
    resp = client.get(f"/{bucket}/{key}", headers=headers)
    resp.raise_for_status()
    return resp.content


def s3_list_objects(bucket: str, prefix: str = "") -> list[str]:
    client = get_httpx_client()
    url = f"https://{MINIO_ENDPOINT}/{quote(bucket)}?prefix={quote(prefix)}"
    headers = _sign_request("GET", url)
    resp = client.get(f"/{bucket}", params={"prefix": prefix}, headers=headers)
    resp.raise_for_status()
    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.text)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    return [c.find("s3:Key", ns).text for c in root.findall(".//s3:Contents", ns)]
