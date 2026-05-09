from fastapi import FastAPI

from app.config.database import Base, engine

from app.models.inference_job import InferenceJob

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Mini RAG Backend Running"}
