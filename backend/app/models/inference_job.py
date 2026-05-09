from sqlalchemy import Column, Integer, Text
from app.config.database import Base


class InferenceJob(Base):
    __tablename__ = "inference_jobs"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(Text, nullable=False)

    status = Column(Text, default="pending")
