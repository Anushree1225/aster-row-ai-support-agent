import json
from pathlib import Path
from typing import Any

import numpy as np

from .embeddings import embed_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / "data" / "vector_index.json"


def load_index() -> list[dict[str, Any]]:
    """Load the locally stored vector index."""

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "Vector index not found. Run: python -m app.rag.ingest"
        )

    return json.loads(
        INDEX_PATH.read_text(encoding="utf-8")
    )


def cosine_similarity(
    query_vector: list[float],
    document_vector: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    query = np.array(query_vector, dtype=np.float32)
    document = np.array(document_vector, dtype=np.float32)

    denominator = (
        np.linalg.norm(query) * np.linalg.norm(document)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(query, document) / denominator
    )


def is_customer_safe_document(
    document: dict[str, Any],
) -> bool:
    """
    Determine whether a document is allowed to provide
    customer-facing policy information.

    Only active, official, customer-facing documents are
    considered authoritative.
    """

    metadata = document.get("metadata", {})

    status = metadata.get("status")
    authority = metadata.get("policy_authority")
    audience = metadata.get("audience")

    return (
        status == "active"
        and authority == "official"
        and audience == "customer"
    )


def retrieve(
    query: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant customer-safe knowledge-base chunks.

    Internal, draft, and superseded documents are excluded before
    similarity ranking.
    """

    index = load_index()

    query_embedding = embed_text(query)

    results = []

    for document in index:

        # ---------------------------------------------------------
        # SAFETY FILTER
        # ---------------------------------------------------------
        if not is_customer_safe_document(document):
            continue

        score = cosine_similarity(
            query_embedding,
            document["embedding"],
        )

        results.append(
            {
                "score": score,
                "chunk_id": document["chunk_id"],
                "source": document["source"],
                "text": document["text"],
                "metadata": document["metadata"],
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]