from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from .tag import TagResponse

# We define HttpUrl so it enforces http:// or https:// formats
class BookmarkBase(BaseModel):
    # Validation: Title cannot be empty
    title: str = Field(..., min_length=1)
    
    # Validation: Strict URL check
    url: HttpUrl
    
    description: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    # Optional list of tags added during creation
    tags: Optional[List[str]] = Field(default_factory=list)

class BookmarkUpdate(BaseModel):
    # All fields are optional for partial updates
    title: Optional[str] = Field(None, min_length=1)
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    # We embed the TagResponse schema so it returns the associated tags
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
