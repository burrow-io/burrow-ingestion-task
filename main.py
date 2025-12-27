# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "boto3",
#     "llama-index-core",
#     "llama-index-embeddings-bedrock",
#     "llama-index-readers-docling",
#     "llama-index-node-parser-docling",
#     "llama-index-vector-stores-postgres",
#     "onnxruntime",
#     "psycopg2-binary",
#     "requests",
#     "transformers",
# ]
# ///

from events.events import main_with_status
from utils.logger import log_info
from utils.config import DOCUMENT_ID, EVENT_TYPE, BUCKET_NAME, S3_KEY, TABLE_NAME

if __name__ == "__main__":
    log_info(
        "Ingestion task starting",
        document_id=DOCUMENT_ID,
        event_type=EVENT_TYPE,
        bucket=BUCKET_NAME,
        key=S3_KEY,
        table_name=TABLE_NAME,
    )
    main_with_status()
