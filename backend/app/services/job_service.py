from pathlib import Path

from sqlalchemy.orm import Session

from app.models.inference_job import InferenceJob
from app.models.document_chunk import DocumentChunk


def get_job_by_filename(db: Session, filename: str):

    return db.query(InferenceJob).filter(
        InferenceJob.filename == filename
    ).first()


def create_job(db: Session, filename: str):

    job = InferenceJob(
        filename=filename
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    return job


def get_job_by_id(db: Session, job_id: int):

    return db.query(InferenceJob).filter(
        InferenceJob.id == job_id
    ).first()


def get_jobs(db: Session):

    return db.query(InferenceJob).all()


def delete_job(db: Session, job_id: int) -> bool:
    job = db.query(InferenceJob).filter(InferenceJob.id == job_id).first()
    if not job:
        return False

    # Delete associated chunks
    db.query(DocumentChunk).filter(DocumentChunk.job_id == job_id).delete()

    # Delete uploaded file
    upload_path = Path("app/uploads") / job.filename
    if upload_path.exists():
        upload_path.unlink()

    db.delete(job)
    db.commit()
    return True
