"""Integration tests for /categories endpoints."""

from app.services.category_service import create_category


class TestListCategories:
    def test_empty(self, client):
        res = client.get("/categories")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_all(self, client, db):
        create_category(db, "ML")
        create_category(db, "CV")
        res = client.get("/categories")
        assert res.status_code == 200
        names = [c["name"] for c in res.json()]
        assert "ML" in names
        assert "CV" in names


class TestCreateCategory:
    def test_creates_category(self, client):
        res = client.post("/categories", json={"name": "NLP"})
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "NLP"
        assert data["id"] is not None

    def test_default_color(self, client):
        res = client.post("/categories", json={"name": "Bio"})
        assert res.json()["color"] == "#6366f1"

    def test_custom_color(self, client):
        res = client.post("/categories", json={"name": "Bio", "color": "#ff0000"})
        assert res.json()["color"] == "#ff0000"


class TestRenameCategory:
    def test_renames(self, client, db):
        cat = create_category(db, "Old")
        res = client.patch(f"/categories/{cat.id}", json={"name": "New"})
        assert res.status_code == 200
        assert res.json()["name"] == "New"

    def test_not_found(self, client):
        res = client.patch("/categories/9999", json={"name": "X"})
        assert res.status_code == 404


class TestDeleteCategory:
    def test_deletes(self, client, db):
        cat = create_category(db, "Temp")
        res = client.delete(f"/categories/{cat.id}")
        assert res.status_code == 204
        # Confirm gone
        assert client.get("/categories").json() == []

    def test_not_found(self, client):
        res = client.delete("/categories/9999")
        assert res.status_code == 404
