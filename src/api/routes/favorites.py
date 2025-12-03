# File: src/api/routes/favorites.py
"""
관심상품 API 라우트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from src.database.db import get_db
from src.models.favorite_product import FavoriteProduct
from src.api.routes.auth import get_current_user
from src.models.user import User


router = APIRouter()


# Pydantic 스키마
class FavoriteProductCreate(BaseModel):
    title: str
    url: str


class FavoriteProductUpdate(BaseModel):
    title: str
    url: str


class FavoriteProductResponse(BaseModel):
    id: int
    title: str
    url: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[FavoriteProductResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 모든 관심상품 조회"""
    favorites = db.query(FavoriteProduct).filter(
        FavoriteProduct.user_id == current_user.id
    ).order_by(FavoriteProduct.created_at.desc()).all()
    
    return favorites


@router.post("/", response_model=FavoriteProductResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    favorite_data: FavoriteProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 관심상품 추가"""
    # 제목과 URL 검증
    if not favorite_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="제목을 입력해주세요"
        )
    
    if not favorite_data.url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL을 입력해주세요"
        )
    
    # 새 관심상품 생성
    new_favorite = FavoriteProduct(
        user_id=current_user.id,
        title=favorite_data.title.strip(),
        url=favorite_data.url.strip()
    )
    
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    
    return new_favorite


@router.put("/{favorite_id}", response_model=FavoriteProductResponse)
async def update_favorite(
    favorite_id: int,
    favorite_data: FavoriteProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관심상품 수정"""
    # 관심상품 조회
    favorite = db.query(FavoriteProduct).filter(
        FavoriteProduct.id == favorite_id,
        FavoriteProduct.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="관심상품을 찾을 수 없습니다"
        )
    
    # 제목과 URL 검증
    if not favorite_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="제목을 입력해주세요"
        )
    
    if not favorite_data.url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL을 입력해주세요"
        )
    
    # 업데이트
    favorite.title = favorite_data.title.strip()
    favorite.url = favorite_data.url.strip()
    
    db.commit()
    db.refresh(favorite)
    
    return favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관심상품 삭제"""
    # 관심상품 조회
    favorite = db.query(FavoriteProduct).filter(
        FavoriteProduct.id == favorite_id,
        FavoriteProduct.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="관심상품을 찾을 수 없습니다"
        )
    
    db.delete(favorite)
    db.commit()
    
    return None
