from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Primary Relationship: One-to-Many
    # back_populates ensures bidirectional updates with the Bookmark model.
    # cascade="all, delete-orphan" removes bookmarks tightly coupled if a user is wiped.
    bookmarks = relationship("Bookmark", back_populates="owner", cascade="all, delete-orphan")
    
    # Additional Relationship: One-to-Many
    # A user can own multiple tags.
    tags = relationship("Tag", back_populates="owner", cascade="all, delete-orphan")
