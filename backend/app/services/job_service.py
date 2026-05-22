from sqlalchemy.orm import Session

from app.models.inference_job import InferenceJob


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
