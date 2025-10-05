from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PdfSession(BaseModel):
    id: str = Field(alias="_id")
    file_id: str
    filename: str
    uid: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True