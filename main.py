from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS Middleware — allows the frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(bookmark.router)
app.include_router(tag.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Bookmark Manager API by IMAM DZAQHOIR (H071241048)!"}
