from fastapi import FastAPI

app = FastAPI(
    title="Tag-Based Personal Bookmark Manager API",
    description="A personal system to store, manage, and categorize bookmarks.",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to the Bookmark Manager API by IMAM DZAQHOIR!"}
