import ollama

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 500

CHUNK_OVERLAP = 50


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
    """Get embedding vector for a piece of text using Ollama."""

    response = ollama.embed(model=EMBED_MODEL, input=text)

    return response["embeddings"][0]


def store_chunks(db: Session, job_id: int, text: str):
    """Chunk the document, embed each chunk, and store in DB."""

    # Remove existing chunks for this job (in case of re-processing)
    db.query(DocumentChunk).filter(DocumentChunk.job_id == job_id).delete()

    chunks = chunk_text(text)

    print(f"Storing {len(chunks)} chunks for job {job_id}")

    for i, chunk in enumerate(chunks):

        embedding = embed_text(chunk)

        doc_chunk = DocumentChunk(
            job_id=job_id,
            chunk_index=i,
            content=chunk,
            embedding=embedding
        )

        db.add(doc_chunk)

    db.commit()

    print(f"Finished storing chunks for job {job_id}")


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
