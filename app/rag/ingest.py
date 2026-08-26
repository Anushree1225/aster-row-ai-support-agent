import json
import re
from pathlib import Path
from typing import Any

from .embeddings import embed_texts


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge-base"
INDEX_PATH = PROJECT_ROOT / "data" / "vector_index.json"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Extract simple YAML-style frontmatter from a Markdown document."""

    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) != 3:
        return {}, text

    raw_metadata = parts[1].strip()
    content = parts[2].strip()

    metadata: dict[str, str] = {}

    for line in raw_metadata.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()

    return metadata, content


def chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    """Split Markdown content into reasonably sized chunks."""

    sections = re.split(r"\n(?=#)", text)

    chunks: list[str] = []
    current = ""

    for section in sections:
        section = section.strip()

        if not section:
            continue

        if len(current) + len(section) + 2 <= max_chars:
            current = f"{current}\n\n{section}".strip()
        else:
            if current:
                chunks.append(current)

            current = section

    if current:
        chunks.append(current)

    return chunks


def load_documents() -> list[dict[str, Any]]:
    """Load all Markdown documents from the knowledge base."""

    documents = []

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        metadata, content = parse_frontmatter(text)
        chunks = chunk_text(content)

        for index, chunk in enumerate(chunks):
            documents.append(
                {
                    "chunk_id": f"{path.stem}-{index}",
                    "source": path.name,
                    "chunk_index": index,
                    "text": chunk,
                    "metadata": metadata,
                }
            )

    return documents


def build_index() -> None:
    """Build and save the local vector index."""

    documents = load_documents()

    if not documents:
        raise RuntimeError("No Markdown documents found in knowledge-base.")

    texts = [document["text"] for document in documents]

    print(f"Loaded {len(documents)} chunks.")
    print("Generating embeddings...")

    embeddings = embed_texts(texts)

    for document, embedding in zip(documents, embeddings):
        document["embedding"] = embedding

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    INDEX_PATH.write_text(
        json.dumps(documents, indent=2),
        encoding="utf-8",
    )

    print(f"Saved vector index to: {INDEX_PATH}")
    print(f"Total chunks: {len(documents)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")


if __name__ == "__main__":
    build_index()