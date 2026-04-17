from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.user import User
from models.bookmark import Bookmark
from models.tag import Tag
from schemas.bookmark import BookmarkCreate, BookmarkUpdate, BookmarkResponse
from auth.dependencies import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


# ========================
# HELPER: Tag Resolution
# ========================
def resolve_tags(tag_names: List[str], user_id: int, db: Session) -> List[Tag]:
    """
    Given a list of tag name strings, find or create Tags for the current user.

    Logic:
    1. For each tag name, check if the user already owns a tag with that name.
    2. If yes, reuse the existing Tag object.
    3. If no, create a new Tag owned by the user.

    This ensures tags are per-user and never duplicated for the same user.
    """
    resolved = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue

        # Look for existing tag owned by this user
        tag = db.query(Tag).filter(
            Tag.name == name,
            Tag.user_id == user_id
        ).first()

        # Create if it doesn't exist
        if not tag:
            tag = Tag(name=name, user_id=user_id)
            db.add(tag)
            db.flush()  # Flush to get the tag.id assigned

        resolved.append(tag)

    return resolved


# ========================
# HELPER: Ownership Check
# ========================
def get_bookmark_or_404(bookmark_id: int, user_id: int, db: Session) -> Bookmark:
    """
    Fetch a bookmark by ID and validate ownership.

    - Returns the Bookmark if it exists AND belongs to the current user.
    - Raises 404 if the bookmark doesn't exist at all.
    - Raises 403 if the bookmark exists but belongs to another user.
    """
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this bookmark"
        )

    return bookmark


# ========================
# 1. CREATE BOOKMARK
# ========================
@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new bookmark for the authenticated user.

    Flow:
    1. Create the Bookmark record with the current user's ID.
    2. Resolve tag names → Tag objects (find existing or create new).
    3. Associate the resolved tags with the bookmark.
    4. Return the created bookmark with embedded tags.
    """
    # Create the bookmark (url is converted to string for SQLAlchemy storage)
    new_bookmark = Bookmark(
        title=bookmark_data.title,
        url=str(bookmark_data.url),
        description=bookmark_data.description,
        user_id=current_user.id
    )

    db.add(new_bookmark)
    db.flush()  # Flush to get new_bookmark.id before associating tags

    # Resolve and associate tags
    if bookmark_data.tags:
        new_bookmark.tags = resolve_tags(bookmark_data.tags, current_user.id, db)

    db.commit()
    db.refresh(new_bookmark)

    return new_bookmark


# ========================
# 2. GET ALL BOOKMARKS
# ========================
@router.get("/", response_model=List[BookmarkResponse])
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookmarks belonging to the authenticated user.
    Always filtered by user_id — users can ONLY see their own bookmarks.
    """
    bookmarks = db.query(Bookmark).options(joinedload(Bookmark.tags)).filter(
        Bookmark.user_id == current_user.id
    ).order_by(Bookmark.id.desc()).all()

    return bookmarks


# ========================
# 3. GET SINGLE BOOKMARK
# ========================
@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific bookmark by ID.
    Validates that the bookmark exists AND belongs to the current user.
    """
    bookmark = db.query(Bookmark).options(joinedload(Bookmark.tags)).filter(
        Bookmark.id == bookmark_id
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    if bookmark.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this bookmark"
        )
    return bookmark


# ========================
# 4. UPDATE BOOKMARK
# ========================
@router.put("/{bookmark_id}", response_model=BookmarkResponse)
def update_bookmark(
    bookmark_id: int,
    bookmark_data: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing bookmark.

    Flow:
    1. Find the bookmark and verify ownership.
    2. Update title, url, and description fields.
    3. If tags are provided (not None), re-resolve and replace tag associations.
       - tags=None means "don't change tags"
       - tags=[] means "remove all tags"
       - tags=["a","b"] means "set tags to exactly a and b"
    4. Commit and return the updated bookmark.
    """
    bookmark = get_bookmark_or_404(bookmark_id, current_user.id, db)

    # Update basic fields with partial support
    if bookmark_data.title is not None:
        bookmark.title = bookmark_data.title
    if bookmark_data.url is not None:
        bookmark.url = str(bookmark_data.url)
    if bookmark_data.description is not None:
        bookmark.description = bookmark_data.description

    # Update tags only if explicitly provided
    if bookmark_data.tags is not None:
        bookmark.tags = resolve_tags(bookmark_data.tags, current_user.id, db)

    db.commit()
    db.refresh(bookmark)

    return bookmark


# ========================
# 5. DELETE BOOKMARK
# ========================
@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a bookmark by ID.
    Validates ownership before deletion. Returns 204 No Content on success.
    """
    bookmark = get_bookmark_or_404(bookmark_id, current_user.id, db)

    db.delete(bookmark)
    db.commit()

    return None
