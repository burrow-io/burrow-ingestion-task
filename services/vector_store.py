import psycopg2
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import VectorStoreIndex
from utils.logger import log_info, log_exception
from utils.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    TABLE_NAME,
    EMBED_DIM,
    DOCUMENT_ID,
)


def create_vector_store():
    vector_store = PGVectorStore.from_params(
        database=DB_NAME,
        host=DB_HOST,
        password=DB_PASSWORD,
        port=DB_PORT,
        user=DB_USER,
        table_name=TABLE_NAME,
        embed_dim=EMBED_DIM,
        hybrid_search=True,
        text_search_config="english",
        hnsw_kwargs={
            "hnsw_m": 16,
            "hnsw_ef_construction": 64,
            "hnsw_ef_search": 40,
            "hnsw_dist_method": "vector_cosine_ops",
        },
    )
    log_info(
        "Initialized PGVectorStore for ingestion",
        document_id=DOCUMENT_ID,
        table_name=TABLE_NAME,
    )
    return vector_store


def create_embed_model():
    embed_model = BedrockEmbedding(
        model_name="amazon.titan-embed-text-v2:0",
        region_name="us-east-1",
    )
    return embed_model


def delete_embeddings_for_document():
    log_info(
        "Deleting embeddings for document",
        document_id=DOCUMENT_ID,
        table_name=TABLE_NAME,
    )

    embed_model = BedrockEmbedding(
        model_name="amazon.titan-embed-text-v2:0",
        region_name="us-east-1",
    )

    vector_store = PGVectorStore.from_params(
        database=DB_NAME,
        host=DB_HOST,
        password=DB_PASSWORD,
        port=DB_PORT,
        user=DB_USER,
        table_name=TABLE_NAME,
        embed_dim=EMBED_DIM,
        hybrid_search=True,
        text_search_config="english",
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )

    try:
        log_info(
            "Calling delete_ref_doc",
            document_id=DOCUMENT_ID,
        )
        index.delete_ref_doc(DOCUMENT_ID, delete_from_docstore=True)
        log_info(
            "delete_ref_doc completed",
            document_id=DOCUMENT_ID,
        )
    except Exception:
        log_exception(
            "delete_ref_doc failed, falling back to SQL delete",
            document_id=DOCUMENT_ID,
            table_name=TABLE_NAME,
        )
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cur = conn.cursor()
        sql = f"DELETE FROM data_{TABLE_NAME} WHERE metadata->>'file_name' LIKE %s"
        cur.execute(sql, (f"%{DOCUMENT_ID}%",))
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        log_info(
            "SQL fallback delete completed",
            document_id=DOCUMENT_ID,
            deleted_count=deleted_count,
        )
