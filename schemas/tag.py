from pydantic import BaseModel, Field
from datetime import datetime

class TagBase(BaseModel):
    # Validation: Title cannot be empty, minimum length 1 securely checks this
    name: str = Field(..., min_length=1, max_length=50)

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
