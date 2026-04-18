from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from .tag import TagResponse

class BookmarkBase(BaseModel):
    title: str = Field(..., min_length=1)
    
    url: HttpUrl
    
    description: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    tags: Optional[List[str]] = Field(default_factory=list)

class BookmarkUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
