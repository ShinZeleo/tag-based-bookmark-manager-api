from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from models.association import bookmark_tag
import datetime

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Ownership: strictly binds the bookmark to a specific User.
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Primary Relationship: One-to-Many
    owner = relationship("User", back_populates="bookmarks")
    
    # Advanced Feature: Many-to-Many Relationship with Tags
    # `secondary` points to our association table
    tags = relationship("Tag", secondary=bookmark_tag, back_populates="bookmarks")
