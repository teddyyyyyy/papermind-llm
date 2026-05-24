from pydantic import BaseModel
from datetime import datetime


class JobResponse(BaseModel):

    id: int

    filename: str

    status: str

    summary: str | None

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
