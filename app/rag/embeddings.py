import os
from typing import List

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"


def embed_text(text: str) -> List[float]:
    """Generate an embedding for a single text."""

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return response.embeddings[0].values


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""

    if not texts:
        return []

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
    )

    return [embedding.values for embedding in response.embeddings]