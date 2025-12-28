import os
from pathlib import Path
from utils.logger import log_info

BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_KEY = os.environ["S3_OBJECT_KEY"]
TABLE_NAME = "burrow_table_hybrid2"
EMBED_DIM = 1024
INGESTION_API_TOKEN = os.environ["INGESTION_API_TOKEN"]
DOCUMENT_ID = Path(S3_KEY).stem
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
ALB_BASE_URL = os.environ["ALB_BASE_URL"]
EVENT_TYPE = os.environ.get("EVENT_TYPE", "Object Created")
MAX_TOKENS = 4096
TOKENIZER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
ORIGIN_VERIFY_TOKEN = os.environ["ORIGIN_VERIFY_TOKEN"]

log_info(
    "Ingestion script loaded",
    document_id=DOCUMENT_ID,
    bucket=BUCKET_NAME,
    key=S3_KEY,
    table_name=TABLE_NAME,
    event_type=EVENT_TYPE,
)
