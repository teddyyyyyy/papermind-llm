from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime, timezone
from app.config.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(Text, nullable=False)

    color = Column(Text, default="#6366f1")  # tailwind indigo-500

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
