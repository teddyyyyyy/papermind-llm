from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime, timezone
from app.config.database import Base


class InferenceJob(Base):
    __tablename__ = "inference_jobs"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(Text, nullable=False)

    status = Column(Text, default="pending")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
