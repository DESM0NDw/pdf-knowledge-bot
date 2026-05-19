import uuid
import httpx
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION = "handbook"
VECTOR_SIZE = 768  # nomic-embed-text
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100


def get_embedding(text: str, ollama_host: str) -> list[float]:
    resp = httpx.post(
        f"http://{ollama_host}:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def chunk_text(text: str, page: int) -> list[dict]:
    chunks = []
    start = 0
    while start < len(text):
        piece = text[start : start + CHUNK_SIZE]
        if piece.strip():
            chunks.append({"text": piece, "page": page})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def index_pdf(pdf_path: str, client: QdrantClient, ollama_host: str) -> int:
    reader = PdfReader(pdf_path)

    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    points = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk in chunk_text(text, page_num):
            vector = get_embedding(chunk["text"], ollama_host)
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"text": chunk["text"], "page": chunk["page"]},
                )
            )

    if points:
        client.upsert(collection_name=COLLECTION, points=points)

    return len(points)


def search(question: str, client: QdrantClient, ollama_host: str, top_k: int = 5) -> list[dict]:
    vector = get_embedding(question, ollama_host)
    hits = client.search(collection_name=COLLECTION, query_vector=vector, limit=top_k)
    return [{"text": h.payload["text"], "page": h.payload["page"], "score": h.score} for h in hits]
