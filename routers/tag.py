from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.tag import Tag
from schemas.tag import TagCreate, TagUpdate, TagResponse
from auth.dependencies import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])

def get_tag_or_404(tag_id: int, user_id: int, db: Session) -> Tag:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    if tag.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tag")
    return tag

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    name = tag_data.name.strip().lower()
    
    existing = db.query(Tag).filter(Tag.name == name, Tag.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")

    new_tag = Tag(name=name, user_id=current_user.id)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.get("/", response_model=List[TagResponse])
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Tag).filter(Tag.user_id == current_user.id).all()

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag = get_tag_or_404(tag_id, current_user.id, db)
    
    new_name = tag_data.name.strip().lower()
    
    if new_name != tag.name:
        existing = db.query(Tag).filter(Tag.name == new_name, Tag.user_id == current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag name already exists")
    
    tag.name = new_name
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag = get_tag_or_404(tag_id, current_user.id, db)
    db.delete(tag)
    db.commit()
    return None
