from sqlalchemy import Column, Integer, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from app.config.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("inference_jobs.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    embedding = Column(Vector(768))
