from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from pathlib import Path

import shutil

from sqlalchemy.orm import Session

from app.config.database import get_db

from app.schemas.inference_job import JobResponse, AskRequest, AskResponse

from app.services.job_service import create_job, get_job_by_filename, get_job_by_id

from app.services.rag_service import search_chunks

from app.models.inference_job import InferenceJob

from openai import OpenAI

client = OpenAI()

LLM_MODEL = "gpt-5.4-mini"

router = APIRouter()

UPLOAD_DIR = Path("app/uploads")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/jobs", response_model=JobResponse)
def create_new_job(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    existing_job = get_job_by_filename(db, file.filename)

    if existing_job:
        return existing_job

    upload_path = UPLOAD_DIR / file.filename

    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = create_job(db, file.filename)

    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = get_job_by_id(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):

    return db.query(InferenceJob).all()


@router.post("/jobs/{job_id}/ask", response_model=AskResponse)
def ask_question(job_id: int, request: AskRequest, db: Session = Depends(get_db)):

    job = get_job_by_id(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "finished":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not finished yet (status: {job.status})"
        )

    # Find the most relevant chunks for the question
    relevant_chunks = search_chunks(db, job_id, request.question)

    context = "\n\n".join(relevant_chunks)

    # Ask the LLM with the retrieved context
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"""Answer the question based only on the following context from a research paper.
If the answer is not in the context, say "I could not find the answer in the document."

Context:
{context}

Question: {request.question}

Answer:"""
            }
        ]
    )

    answer = response.choices[0].message.content

    return AskResponse(
        job_id=job_id,
        question=request.question,
        answer=answer
    )
