"""Integration tests for /jobs endpoints."""

import io
from unittest.mock import MagicMock, patch

from app.services.job_service import create_job


class TestListJobs:
    def test_empty(self, client):
        res = client.get("/jobs")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_created_jobs(self, client, db):
        create_job(db, "a.pdf")
        create_job(db, "b.pdf")
        res = client.get("/jobs")
        assert res.status_code == 200
        assert len(res.json()) == 2


class TestGetJob:
    def test_not_found(self, client):
        res = client.get("/jobs/9999")
        assert res.status_code == 404

    def test_found(self, client, db):
        job = create_job(db, "paper.pdf")
        res = client.get(f"/jobs/{job.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == job.id
        assert data["filename"] == "paper.pdf"
        assert data["status"] == "pending"


class TestUploadFile:
    def test_upload_creates_job(self, client, tmp_path):
        content = b"%PDF fake pdf content"
        res = client.post(
            "/jobs",
            files={"file": ("test.pdf", io.BytesIO(content), "application/pdf")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["filename"] == "test.pdf"
        assert data["status"] == "pending"

    def test_duplicate_upload_returns_existing(self, client, tmp_path):
        content = b"hello"
        files = {"file": ("dup.txt", io.BytesIO(content), "text/plain")}
        res1 = client.post("/jobs", files=files)
        files = {"file": ("dup.txt", io.BytesIO(content), "text/plain")}
        res2 = client.post("/jobs", files=files)
        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res1.json()["id"] == res2.json()["id"]


class TestUpdateJob:
    def test_assign_category(self, client, db):
        from app.services.category_service import create_category
        job = create_job(db, "paper.pdf")
        cat = create_category(db, "ML")
        res = client.patch(f"/jobs/{job.id}", json={"category_id": cat.id})
        assert res.status_code == 200
        assert res.json()["category_id"] == cat.id

    def test_unassign_category(self, client, db):
        from app.services.category_service import create_category
        job = create_job(db, "paper.pdf")
        cat = create_category(db, "ML")
        job.category_id = cat.id
        db.commit()

        res = client.patch(f"/jobs/{job.id}", json={"category_id": None})
        assert res.status_code == 200
        assert res.json()["category_id"] is None

    def test_not_found(self, client):
        res = client.patch("/jobs/9999", json={"category_id": None})
        assert res.status_code == 404


class TestDeleteJob:
    def test_deletes_existing_job(self, client, db):
        job = create_job(db, "bye.pdf")
        res = client.delete(f"/jobs/{job.id}")
        assert res.status_code == 204
        # Confirm it's gone
        assert client.get(f"/jobs/{job.id}").status_code == 404

    def test_not_found(self, client):
        res = client.delete("/jobs/9999")
        assert res.status_code == 404


class TestAskQuestion:
    def test_job_not_found(self, client):
        res = client.post("/jobs/9999/ask", json={"question": "What is this?"})
        assert res.status_code == 404

    def test_job_not_finished(self, client, db):
        job = create_job(db, "pending.pdf")  # status = "pending"
        res = client.post(f"/jobs/{job.id}/ask", json={"question": "hello"})
        assert res.status_code == 400
        assert "not finished" in res.json()["detail"]

    def test_finished_job_returns_answer(self, client, db):
        job = create_job(db, "done.pdf")
        job.status = "finished"
        db.commit()

        mock_answer = "The answer is 42."

        # Mock search_chunks so it doesn't hit pgvector
        with patch("app.routers.jobs.search_chunks", return_value=["Some relevant context"]):
            # Mock the OpenAI completion
            mock_response = MagicMock()
            mock_response.choices[0].message.content = mock_answer
            with patch("app.routers.jobs.client.chat.completions.create", return_value=mock_response):
                res = client.post(f"/jobs/{job.id}/ask", json={"question": "What is 6×7?"})

        assert res.status_code == 200
        data = res.json()
        assert data["job_id"] == job.id
        assert data["question"] == "What is 6×7?"
        assert data["answer"] == mock_answer
