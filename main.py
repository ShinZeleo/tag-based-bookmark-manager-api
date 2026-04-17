from fastapi import FastAPI
from database import engine, Base
from routers import auth, bookmark, tag

# Create all database tables on startup
# This reads all models that inherit from Base and generates corresponding SQL tables.
from models import User, Bookmark, Tag
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tag-Based Personal Bookmark Manager API",
    description="A personal system to store, manage, and categorize bookmarks (URLs) per user, with tagging functionality.",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(bookmark.router)
app.include_router(tag.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Bookmark Manager API by IMAM DZAQHOIR (H071241048)!"}
