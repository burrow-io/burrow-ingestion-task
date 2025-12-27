from transformers import AutoTokenizer
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from utils.logger import log_info
from utils.config import MAX_TOKENS, TOKENIZER_MODEL, DOCUMENT_ID, BUCKET_NAME, S3_KEY


def create_hybrid_chunker():
    log_info(
        "Creating HybridChunker",
        document_id=DOCUMENT_ID,
        max_tokens=MAX_TOKENS,
        tokenizer_model=TOKENIZER_MODEL,
    )

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(TOKENIZER_MODEL),
        max_tokens=MAX_TOKENS,
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,
    )

    log_info("HybridChunker initialized", document_id=DOCUMENT_ID)
    return chunker


def clean_node_metadata(nodes):
    for idx, node in enumerate(nodes):
        old_meta = node.metadata
        clean_meta = {}

        if "origin" in old_meta and "filename" in old_meta["origin"]:
            clean_meta["file_name"] = old_meta["origin"]["filename"]

        clean_meta["doc_id"] = DOCUMENT_ID
        clean_meta["source"] = f"s3://{BUCKET_NAME}/{S3_KEY}"

        if "doc_items" in old_meta and old_meta["doc_items"]:
            first_item = old_meta["doc_items"][0]
            if "prov" in first_item and first_item["prov"]:
                clean_meta["page"] = first_item["prov"][0].get("page_no")
            if "label" in first_item:
                clean_meta["content_type"] = first_item["label"]

        clean_meta["chunk_index"] = idx
        clean_meta["total_chunks"] = len(nodes)

        node.metadata = clean_meta

    log_info(
        "Metadata cleaned",
        document_id=DOCUMENT_ID,
        sample=nodes[0].metadata if nodes else {},
    )

    return nodes
