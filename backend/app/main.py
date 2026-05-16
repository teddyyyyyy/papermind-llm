from fastapi import FastAPI

from app.config.database import Base, engine

from app.models.inference_job import InferenceJob

from app.routers.jobs import router as jobs_router

app = FastAPI()

app.include_router(jobs_router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Mini RAG Backend Running"}
