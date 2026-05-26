"""Unit tests for app/services/job_service.py"""

from app.models.inference_job import InferenceJob
from app.models.document_chunk import DocumentChunk
from app.services.job_service import (
    create_job,
    get_job_by_id,
    get_job_by_filename,
    get_jobs,
    delete_job,
)


class TestCreateJob:
    def test_creates_job_with_filename(self, db):
        job = create_job(db, "paper.pdf")
        assert job.id is not None
        assert job.filename == "paper.pdf"

    def test_default_status_is_pending(self, db):
        job = create_job(db, "paper.pdf")
        assert job.status == "pending"

    def test_created_at_is_set(self, db):
        job = create_job(db, "paper.pdf")
        assert job.created_at is not None


class TestGetJobById:
    def test_returns_job_when_found(self, db):
        created = create_job(db, "test.pdf")
        found = get_job_by_id(db, created.id)
        assert found is not None
        assert found.id == created.id

    def test_returns_none_when_not_found(self, db):
        result = get_job_by_id(db, 9999)
        assert result is None


class TestGetJobByFilename:
    def test_returns_job_when_found(self, db):
        create_job(db, "unique.pdf")
        found = get_job_by_filename(db, "unique.pdf")
        assert found is not None
        assert found.filename == "unique.pdf"

    def test_returns_none_when_not_found(self, db):
        result = get_job_by_filename(db, "ghost.pdf")
        assert result is None


class TestGetJobs:
    def test_returns_empty_list_when_no_jobs(self, db):
        assert get_jobs(db) == []

    def test_returns_all_jobs(self, db):
        create_job(db, "a.pdf")
        create_job(db, "b.pdf")
        jobs = get_jobs(db)
        assert len(jobs) == 2


class TestDeleteJob:
    def test_deletes_existing_job(self, db):
        job = create_job(db, "delete_me.pdf")
        result = delete_job(db, job.id)
        assert result is True
        assert get_job_by_id(db, job.id) is None

    def test_returns_false_for_missing_job(self, db):
        result = delete_job(db, 9999)
        assert result is False

    def test_deletes_associated_chunks(self, db):
        job = create_job(db, "with_chunks.pdf")
        # Insert a fake chunk
        chunk = DocumentChunk(job_id=job.id, chunk_index=0, content="hello", embedding=None)
        db.add(chunk)
        db.commit()

        delete_job(db, job.id)

        remaining = db.query(DocumentChunk).filter(DocumentChunk.job_id == job.id).all()
        assert remaining == []
