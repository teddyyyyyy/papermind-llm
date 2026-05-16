from sqlalchemy.orm import Session

from app.models.inference_job import InferenceJob


def create_job(db: Session, filename: str):

    job = InferenceJob(
        filename=filename
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    return job


def get_jobs(db: Session):

    return db.query(InferenceJob).all()
