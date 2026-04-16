from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Provide the Database URL
# We are using SQLite, so this creates a file named 'bookmark_manager.db' in the project root.
SQLALCHEMY_DATABASE_URL = "sqlite:///./bookmark_manager.db"

# 2. Setup the SQLAlchemy Engine
# The Engine is the starting point for any SQLAlchemy application.
# `connect_args={"check_same_thread": False}` is REQUIRED for SQLite in FastAPI.
# This is because FastAPI can use multiple threads to handle requests,
# and SQLite by default does not allow multiple threads to access the same connection.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a SessionLocal class
# Each instance of the SessionLocal class will be a database session.
# - autoflush=False: We manually control when data is sent to the DB.
# - autocommit=False: We manually commit to support database transactions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Declarative Base class
# All database models (User, Bookmark, Tag) will inherit from this class.
# This links our Python class definitions to SQLAlchemy's Table objects under the hood.
Base = declarative_base()

# 5. Dependency for Database Sessions
# This function creates a new session per request and closes it after the request finishes.
# It uses the `yield` generator to let FastAPI handle the tearing down, keeping database connections clean.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
