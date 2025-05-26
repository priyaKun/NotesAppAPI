from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="My Note")
    content: str = Field(..., min_length=1, example="This is my note content")

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, example="Updated Note")
    content: Optional[str] = Field(None, min_length=1, example="Updated content")

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }