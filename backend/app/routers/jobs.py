from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from pathlib import Path

import shutil

from sqlalchemy.orm import Session

from app.config.database import SessionLocal

from app.schemas.inference_job import JobResponse

from app.services.job_service import create_job, get_job_by_filename, get_job_by_id

from app.models.inference_job import InferenceJob

router = APIRouter()

UPLOAD_DIR = Path("app/uploads")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/jobs",
    response_model=JobResponse
)
def create_new_job(
    file: UploadFile = File(...)
):

    db: Session = SessionLocal()

    existing_job = get_job_by_filename(db, file.filename)

    if existing_job:
        return existing_job

    upload_path = UPLOAD_DIR / file.filename

    with open(upload_path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    job = create_job(
        db,
        file.filename
    )

    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int):

    db: Session = SessionLocal()

    job = get_job_by_id(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/jobs")
def get_jobs():

    db: Session = SessionLocal()

    jobs = db.query(InferenceJob).all()

    return jobs
