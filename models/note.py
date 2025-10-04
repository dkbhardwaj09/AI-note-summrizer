from pydantic import BaseModel, Field
from typing import Optional

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    desc: str = Field(..., min_length=1)
    important: Optional[bool] = False

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    desc: Optional[str] = Field(None, min_length=1)
    important: Optional[bool] = None

class NoteInDB(NoteBase):
    id: str = Field(alias="_id")
    uid: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True