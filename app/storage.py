import boto3
import botocore.httpsession
from app.config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from app.certs_setup import ensure_certs, get_cert_paths


def get_minio_client():
    ensure_certs()
    certs = get_cert_paths()

    http_session = botocore.httpsession.URLLib3Session(
        verify=False,
        client_cert=(certs["cert_file"], certs["key_file"]),
    )

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        verify=False,
    )
    client._endpoint._http_session = http_session
    return client
