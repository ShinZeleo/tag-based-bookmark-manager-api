from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

# Association Table for Many-to-Many Relationship between Bookmarks and Tags.
# We use a Table instead of a class Model because we don't need independent instances.
bookmark_tag = Table(
    "bookmark_tags",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)
