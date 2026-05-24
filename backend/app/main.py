from contextlib import asynccontextmanager

from threading import Thread

from fastapi import FastAPI

from sqlalchemy import text

from app.config.database import Base, engine

from app.models.inference_job import InferenceJob
from app.models.document_chunk import DocumentChunk

from app.routers.jobs import router as jobs_router

from app.worker.job_worker import process_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Enable pgvector extension and create all tables
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    # Start the job worker in a background thread
    worker_thread = Thread(target=process_jobs, daemon=True)
    worker_thread.start()

    print("✅ Job worker started in background")

    yield

    # Shutdown — daemon thread stops automatically with the app
    print("🛑 Shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(jobs_router)


@app.get("/")
def root():
    return {"message": "Mini RAG Backend Running"}
