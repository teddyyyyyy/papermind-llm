from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime, timezone
from app.config.database import Base


class InferenceJob(Base):
    __tablename__ = "inference_jobs"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(Text, nullable=False)

    title = Column(Text, nullable=True)

    status = Column(Text, default="pending")

    summary = Column(Text, nullable=True)

    category_id = Column(Integer, nullable=True)  # FK to categories.id

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
