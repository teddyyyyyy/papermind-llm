from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from pathlib import Path

import shutil

from sqlalchemy.orm import Session

from app.config.database import SessionLocal

from app.schemas.inference_job import JobResponse

from app.services.job_service import create_job

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

    upload_path = UPLOAD_DIR / file.filename

    with open(upload_path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    db: Session = SessionLocal()

    job = create_job(
        db,
        file.filename
    )

    return job


@router.get("/jobs")
def get_jobs():

    db: Session = SessionLocal()

    jobs = db.query(InferenceJob).all()

    return jobs
