from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "postgresql://teddy:password@localhost:5555/mini_rag_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Dependency that provides a DB session and always closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
