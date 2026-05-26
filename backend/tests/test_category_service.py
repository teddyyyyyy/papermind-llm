"""Unit tests for app/services/category_service.py"""

from app.services.category_service import (
    create_category,
    get_categories,
    update_category,
    delete_category,
)
from app.services.job_service import create_job
from app.models.inference_job import InferenceJob


class TestCreateCategory:
    def test_creates_with_name(self, db):
        cat = create_category(db, "ML Papers")
        assert cat.id is not None
        assert cat.name == "ML Papers"

    def test_default_color(self, db):
        cat = create_category(db, "Physics")
        assert cat.color == "#6366f1"

    def test_custom_color(self, db):
        cat = create_category(db, "Bio", color="#10b981")
        assert cat.color == "#10b981"


class TestGetCategories:
    def test_empty_list_initially(self, db):
        assert get_categories(db) == []

    def test_returns_all_categories_in_order(self, db):
        create_category(db, "First")
        create_category(db, "Second")
        cats = get_categories(db)
        assert len(cats) == 2
        assert cats[0].name == "First"
        assert cats[1].name == "Second"


class TestUpdateCategory:
    def test_rename(self, db):
        cat = create_category(db, "Old Name")
        updated = update_category(db, cat.id, name="New Name", color=None)
        assert updated.name == "New Name"
        assert updated.color == cat.color  # unchanged

    def test_change_color(self, db):
        cat = create_category(db, "Papers")
        updated = update_category(db, cat.id, name=None, color="#ff0000")
        assert updated.color == "#ff0000"
        assert updated.name == "Papers"  # unchanged

    def test_returns_none_for_missing_category(self, db):
        result = update_category(db, 9999, name="X", color=None)
        assert result is None


class TestDeleteCategory:
    def test_deletes_existing_category(self, db):
        cat = create_category(db, "To Delete")
        result = delete_category(db, cat.id)
        assert result is True
        assert get_categories(db) == []

    def test_returns_false_for_missing_category(self, db):
        result = delete_category(db, 9999)
        assert result is False

    def test_unassigns_jobs_on_delete(self, db):
        cat = create_category(db, "NLP")
        job = create_job(db, "paper.pdf")
        job.category_id = cat.id
        db.commit()

        delete_category(db, cat.id)

        db.refresh(job)
        assert job.category_id is None
