import json
import pickle
from app.storage import s3_put_object, s3_get_object, s3_list_objects
from app.config import MINIO_BUCKET_DSS, MINIO_BUCKET_MODEL


def upload_json(bucket: str, key: str, data: dict):
    json_bytes = json.dumps(data, default=str).encode("utf-8")
    s3_put_object(bucket, key, json_bytes, "application/json")
    return f"{bucket}/{key}"


def download_json(bucket: str, key: str):
    content = s3_get_object(bucket, key)
    return json.loads(content.decode("utf-8"))


def download_model_bytes(bucket: str, key: str):
    return s3_get_object(bucket, key)


def list_objects(bucket: str, prefix: str = ""):
    return s3_list_objects(bucket, prefix)


def upload_prediksi(cabang_id: str, tanggal: str, data: dict):
    key = f"prediksi_{cabang_id}_{tanggal}.json"
    return upload_json(MINIO_BUCKET_DSS, key, data)


def upload_promo(cabang_id: str, tanggal: str, data: dict):
    key = f"promo_{cabang_id}_{tanggal}.json"
    return upload_json(MINIO_BUCKET_DSS, key, data)


def download_model_pkl():
    return download_model_bytes(MINIO_BUCKET_MODEL, "model.pkl")


def download_model():
    return download_model_bytes(MINIO_BUCKET_MODEL, "model.pkl")


def upload_model_pkl(model_dict: dict):
    model_bytes = pickle.dumps(model_dict)
    s3_put_object(MINIO_BUCKET_MODEL, "model.pkl", model_bytes, "application/octet-stream")
