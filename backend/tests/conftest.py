"""
Shared pytest fixtures.

pgvector is mocked at the sys.modules level (before any app code is imported)
so that SQLite can be used as the test database without needing a real
PostgreSQL server or the pgvector extension.
"""

import os
import sys
from unittest.mock import MagicMock

from sqlalchemy import Text

# ── 1. Patch pgvector BEFORE any app module is imported ──────────────────────
# Vector(dim) is replaced with Text() so SQLite understands the column type.
_mock_pgvector_sql = MagicMock()
_mock_pgvector_sql.Vector = lambda dim: Text()
sys.modules.setdefault("pgvector", MagicMock())
sys.modules.setdefault("pgvector.sqlalchemy", _mock_pgvector_sql)

# ── 2. Dummy OpenAI key so the OpenAI() constructor doesn't raise ─────────────
os.environ.setdefault("OPENAI_API_KEY", "test-sk-dummy")

# ── 3. Now safe to import app code ────────────────────────────────────────────
import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.config.database import Base, get_db  # noqa: E402
from app.models.inference_job import InferenceJob  # noqa: E402, F401
from app.models.document_chunk import DocumentChunk  # noqa: E402, F401
from app.models.category import Category  # noqa: E402, F401
from app.routers.jobs import router as jobs_router  # noqa: E402
from app.routers.categories import router as cats_router  # noqa: E402

# ── In-memory SQLite engine (StaticPool keeps one connection for the process) ──
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_db():
    """Create all tables before every test, drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """A SQLAlchemy session pointed at the in-memory test database."""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db, tmp_path, monkeypatch):
    """
    FastAPI TestClient with:
    - DB dependency overridden to use the test session
    - UPLOAD_DIR redirected to a temp directory
    """
    import app.routers.jobs as jobs_module
    monkeypatch.setattr(jobs_module, "UPLOAD_DIR", tmp_path)

    def override_get_db():
        yield db

    test_app = FastAPI()
    test_app.include_router(jobs_router)
    test_app.include_router(cats_router)
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c
