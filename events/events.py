from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser
from llama_index.core.ingestion import IngestionPipeline
from services.s3 import generate_presigned_url, get_s3_deletion_status
from services.document_processing import create_hybrid_chunker, clean_node_metadata
from services.vector_store import (
    create_vector_store,
    create_embed_model,
    delete_embeddings_for_document,
)
from services.api import update_document_status
from utils.logger import log_info, log_exception
from utils.config import BUCKET_NAME, S3_KEY, DOCUMENT_ID, EVENT_TYPE


def run_ingestion_pipeline():
    log_info(
        "Starting ingestion",
        document_id=DOCUMENT_ID,
        bucket=BUCKET_NAME,
        key=S3_KEY,
        table_name="burrow_table_hybrid2",
    )

    presigned_url = generate_presigned_url(BUCKET_NAME, S3_KEY)

    reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)
    docs = reader.load_data(presigned_url)
    log_info(
        "Loaded document from S3",
        document_id=DOCUMENT_ID,
        doc_count=len(docs),
    )

    for doc in docs:
        doc.id_ = DOCUMENT_ID

    hybrid_chunker = create_hybrid_chunker()
    node_parser = DoclingNodeParser(chunker=hybrid_chunker)
    nodes = node_parser.get_nodes_from_documents(docs)
    nodes = clean_node_metadata(nodes)
    log_info(
        "Parsed document into nodes",
        document_id=DOCUMENT_ID,
        node_count=len(nodes),
    )

    vector_store = create_vector_store()
    embed_model = create_embed_model()

    pipeline = IngestionPipeline(
        transformations=[embed_model],
        vector_store=vector_store,
    )

    pipeline.run(nodes=nodes, num_workers=2)
    log_info(
        "Ingestion complete — data stored in Aurora (pgvector)",
        document_id=DOCUMENT_ID,
        node_count=len(nodes),
    )


def main_with_status():
    if EVENT_TYPE == "Object Tags Added":
        deletion_status = get_s3_deletion_status()

        if deletion_status != "deleting":
            log_info(
                "Non-deletion tag event, skipping",
                document_id=DOCUMENT_ID,
                deletion_status=deletion_status,
            )
            return

        log_info(
            "Deletion event detected",
            document_id=DOCUMENT_ID,
            bucket=BUCKET_NAME,
            key=S3_KEY,
        )

        try:
            delete_embeddings_for_document()
            update_document_status("deleted")
            log_info(
                "Deletion completed successfully",
                document_id=DOCUMENT_ID,
            )
        except Exception:
            log_exception(
                "Deletion failed",
                document_id=DOCUMENT_ID,
            )
            try:
                update_document_status("delete_failed")
            except Exception:
                log_exception(
                    "Failed to set status=delete_failed",
                    document_id=DOCUMENT_ID,
                )
            raise

    else:
        log_info(
            "Ingestion event received",
            document_id=DOCUMENT_ID,
            event_type=EVENT_TYPE,
            bucket=BUCKET_NAME,
            key=S3_KEY,
        )

        try:
            update_document_status("running")
            log_info(
                "Document marked as running",
                document_id=DOCUMENT_ID,
            )
        except Exception:
            log_exception(
                "Failed to set status=running",
                document_id=DOCUMENT_ID,
            )

        try:
            run_ingestion_pipeline()
            update_document_status("finished")
            log_info(
                "Ingestion completed successfully",
                document_id=DOCUMENT_ID,
            )
        except Exception:
            log_exception(
                "Ingestion failed",
                document_id=DOCUMENT_ID,
            )
            try:
                update_document_status("failed")
                log_info(
                    "Document marked as failed",
                    document_id=DOCUMENT_ID,
                )
            except Exception:
                log_exception(
                    "Failed to set status=failed",
                    document_id=DOCUMENT_ID,
                )
            raise
