from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobResponse(BaseModel):

    id: int

    filename: str

    title: Optional[str] = None

    status: str

    summary: Optional[str] = None

    category_id: Optional[int] = None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class AskRequest(BaseModel):

    question: str


class AskResponse(BaseModel):

    job_id: int

    question: str

    answer: str


class JobUpdate(BaseModel):

    category_id: Optional[int] = None
