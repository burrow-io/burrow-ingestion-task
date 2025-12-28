import boto3
from utils.logger import log_info, log_exception
from utils.config import BUCKET_NAME, S3_KEY, DOCUMENT_ID


def get_s3_deletion_status():
    log_info(
        "Fetching S3 tags for deletion detection",
        document_id=DOCUMENT_ID,
        bucket=BUCKET_NAME,
        key=S3_KEY,
    )

    s3_client = boto3.client("s3", region_name="us-east-1")
    try:
        response = s3_client.get_object_tagging(Bucket=BUCKET_NAME, Key=S3_KEY)
        tags = {tag["Key"]: tag["Value"] for tag in response["TagSet"]}
        deletion_status = tags.get("deletion_status", None)

        log_info(
            "S3 tags fetched successfully",
            document_id=DOCUMENT_ID,
            deletion_status=deletion_status,
            all_tags=tags,
        )

        return deletion_status
    except Exception:
        log_exception(
            "Failed to fetch S3 tags",
            document_id=DOCUMENT_ID,
            bucket=BUCKET_NAME,
            key=S3_KEY,
        )
        return None


def generate_presigned_url(bucket, key):
    s3 = boto3.client("s3", region_name="us-east-1")
    presigned_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600,
    )
    log_info(
        "Generated presigned S3 URL",
        document_id=DOCUMENT_ID,
        bucket=bucket,
    )
    return presigned_url
