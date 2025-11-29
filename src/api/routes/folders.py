# File: src/api/routes/folders.py
"""
폴더 관리 API 라우트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from src.database.db import get_db
from src.models.user import User
from src.models.folder import Folder
from src.api.routes.auth import get_current_user

router = APIRouter()


# Pydantic 스키마
class FolderCreate(BaseModel):
    name: str


class FolderUpdate(BaseModel):
    name: str


class FolderResponse(BaseModel):
    id: int
    name: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[FolderResponse])
async def get_folders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 폴더 목록 조회"""
    folders = db.query(Folder).filter(Folder.user_id == current_user.id).all()
    return folders


@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """폴더 생성"""
    new_folder = Folder(
        user_id=current_user.id,
        name=folder_data.name
    )
    
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    
    return new_folder


@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """폴더 수정"""
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    folder.name = folder_data.name
    db.commit()
    db.refresh(folder)
    
    return folder


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """폴더 삭제"""
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    db.delete(folder)
    db.commit()
    
    return None
