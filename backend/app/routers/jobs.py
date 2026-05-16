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

    print("STEP 1")

    upload_path = UPLOAD_DIR / file.filename

    print("STEP 2", upload_path)

    with open(upload_path, "wb") as buffer:

        print("STEP 3")

        shutil.copyfileobj(file.file, buffer)

    print("STEP 4")

    db: Session = SessionLocal()

    print("STEP 5")

    job = create_job(
        db,
        file.filename
    )

    print("STEP 6")

    return job
