import requests
from utils.logger import log_info
from utils.config import ALB_BASE_URL, INGESTION_API_TOKEN, ORIGIN_VERIFY_TOKEN, DOCUMENT_ID


def update_document_status(status):
    url = f"{ALB_BASE_URL}/api/documents/{DOCUMENT_ID}"
    headers = {
        "x-api-token": INGESTION_API_TOKEN,
        "X-Origin-Verify": ORIGIN_VERIFY_TOKEN,
    }
    data = {"status": status}

    log_info(
        "Updating document status via management-api",
        document_id=DOCUMENT_ID,
        status=status,
        url=url,
    )

    resp = requests.patch(url, headers=headers, json=data, timeout=60)

    log_info(
        "Document status update response",
        document_id=DOCUMENT_ID,
        status=status,
        http_status=resp.status_code,
        response_body=resp.text[:500],
    )

    resp.raise_for_status()
