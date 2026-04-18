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

def resolve_tags(tag_names: List[str], user_id: int, db: Session) -> List[Tag]:
        resolved = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue

        tag = db.query(Tag).filter(
            Tag.name == name,
            Tag.user_id == user_id
        ).first()

        if not tag:
            tag = Tag(name=name, user_id=user_id)
            db.add(tag)
            db.flush()  # Flush to get the tag.id assigned

        resolved.append(tag)

    return resolved

def get_bookmark_or_404(bookmark_id: int, user_id: int, db: Session) -> Bookmark:
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

@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_bookmark = Bookmark(
        title=bookmark_data.title,
        url=str(bookmark_data.url),
        description=bookmark_data.description,
        user_id=current_user.id
    )

    db.add(new_bookmark)
    db.flush()  # Flush to get new_bookmark.id before associating tags

    if bookmark_data.tags:
        new_bookmark.tags = resolve_tags(bookmark_data.tags, current_user.id, db)

    db.commit()
    db.refresh(new_bookmark)

    return new_bookmark

@router.get("/", response_model=List[BookmarkResponse])
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
        bookmarks = db.query(Bookmark).options(joinedload(Bookmark.tags)).filter(
        Bookmark.user_id == current_user.id
    ).order_by(Bookmark.id.desc()).all()

    return bookmarks

@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

@router.put("/{bookmark_id}", response_model=BookmarkResponse)
def update_bookmark(
    bookmark_id: int,
    bookmark_data: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
        bookmark = get_bookmark_or_404(bookmark_id, current_user.id, db)

    if bookmark_data.title is not None:
        bookmark.title = bookmark_data.title
    if bookmark_data.url is not None:
        bookmark.url = str(bookmark_data.url)
    if bookmark_data.description is not None:
        bookmark.description = bookmark_data.description

    if bookmark_data.tags is not None:
        bookmark.tags = resolve_tags(bookmark_data.tags, current_user.id, db)

    db.commit()
    db.refresh(bookmark)

    return bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
        bookmark = get_bookmark_or_404(bookmark_id, current_user.id, db)

    db.delete(bookmark)
    db.commit()

    return None
