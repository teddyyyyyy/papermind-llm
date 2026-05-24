from fastapi import FastAPI

from sqlalchemy import text

from app.config.database import Base, engine

from app.models.inference_job import InferenceJob
from app.models.document_chunk import DocumentChunk

from app.routers.jobs import router as jobs_router

app = FastAPI()

app.include_router(jobs_router)

# Enable pgvector extension and create all tables
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Mini RAG Backend Running"}
