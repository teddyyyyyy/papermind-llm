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
