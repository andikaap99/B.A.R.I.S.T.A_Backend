import json
from app.storage import get_minio_client
from app.config import MINIO_BUCKET_DSS, MINIO_BUCKET_MODEL


def upload_json(bucket: str, key: str, data: dict):
    client = get_minio_client()
    json_bytes = json.dumps(data, default=str).encode("utf-8")
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json_bytes,
        ContentType="application/json",
    )
    return f"{bucket}/{key}"


def download_json(bucket: str, key: str):
    client = get_minio_client()
    response = client.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return json.loads(content)


def download_model(bucket: str, key: str):
    client = get_minio_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


def list_objects(bucket: str, prefix: str = ""):
    client = get_minio_client()
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj["Key"] for obj in response.get("Contents", [])]


def upload_prediksi(cabang_id: str, tanggal: str, data: dict):
    key = f"prediksi_{cabang_id}_{tanggal}.json"
    return upload_json(MINIO_BUCKET_DSS, key, data)


def upload_promo(cabang_id: str, tanggal: str, data: dict):
    key = f"promo_{cabang_id}_{tanggal}.json"
    return upload_json(MINIO_BUCKET_DSS, key, data)


def download_model_pkl():
    return download_model(MINIO_BUCKET_MODEL, "model.pkl")
