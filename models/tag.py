from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from models.association import bookmark_tag
import datetime

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Ownership: tags belong to a specific user as well.
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationship to User
    owner = relationship("User", back_populates="tags")
    
    # Advanced Feature: Many-to-Many Relationship with Bookmarks
    # `secondary` points to our association table
    bookmarks = relationship("Bookmark", secondary=bookmark_tag, back_populates="tags")
