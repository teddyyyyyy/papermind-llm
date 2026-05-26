from contextlib import asynccontextmanager

from threading import Thread

from fastapi import FastAPI

from sqlalchemy import text

from app.config.database import Base, engine

from app.models.inference_job import InferenceJob
from app.models.document_chunk import DocumentChunk
from app.models.category import Category

from app.routers.jobs import router as jobs_router
from app.routers.categories import router as categories_router

from app.worker.job_worker import process_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):

    with engine.connect() as conn:
        # pgvector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create all new tables (categories, etc.)
        conn.commit()

    Base.metadata.create_all(bind=engine)

    # Add new columns to inference_jobs if they don't exist yet (idempotent migration)
    with engine.connect() as conn:
        conn.execute(text(
            "ALTER TABLE inference_jobs ADD COLUMN IF NOT EXISTS title TEXT"
        ))
        conn.execute(text(
            "ALTER TABLE inference_jobs ADD COLUMN IF NOT EXISTS category_id INTEGER"
        ))
        conn.commit()

    # Start the job worker in a background thread
    worker_thread = Thread(target=process_jobs, daemon=True)
    worker_thread.start()

    print("✅ Job worker started in background")

    yield

    print("🛑 Shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(jobs_router)
app.include_router(categories_router)


@app.get("/")
def root():
    return {"message": "Mini RAG Backend Running"}
