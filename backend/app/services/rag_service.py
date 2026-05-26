from openai import OpenAI

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


client = OpenAI()  # reads OPENAI_API_KEY from environment

EMBED_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 1500   # ~375 tokens — better context per chunk, fewer total chunks

CHUNK_OVERLAP = 150


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""

    chunks = []

    start = 0

    while start < len(text):

        end = min(start + CHUNK_SIZE, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def embed_text(text: str) -> list[float]:
    """Embed a single string (used for query embedding at search time)."""

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )

    return response.data[0].embedding


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed all chunks in ONE API call instead of one call per chunk."""

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )

    # response.data is ordered to match input order
    return [item.embedding for item in response.data]


def store_chunks(db: Session, job_id: int, text: str):
    """Chunk the document, batch-embed all chunks, and store in DB."""

    db.query(DocumentChunk).filter(DocumentChunk.job_id == job_id).delete()

    chunks = chunk_text(text)

    print(f"Embedding {len(chunks)} chunks in one batch call...")

    embeddings = embed_batch(chunks)   # 1 API call instead of N

    db.add_all([
        DocumentChunk(
            job_id=job_id,
            chunk_index=i,
            content=chunk,
            embedding=embedding,
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ])

    db.commit()

    print(f"Finished storing {len(chunks)} chunks for job {job_id}")


def search_chunks(db: Session, job_id: int, question: str, top_k: int = 5) -> list[str]:
    """Find the most relevant chunks for a question using cosine similarity."""

    query_embedding = embed_text(question)

    results = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.job_id == job_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    return [r.content for r in results]
