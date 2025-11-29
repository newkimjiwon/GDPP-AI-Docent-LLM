# File: src/api/routes/conversations.py
"""
대화 관리 API 라우트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.database.db import get_db
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.api.routes.auth import get_current_user

router = APIRouter()


# Pydantic 스키마
class ConversationCreate(BaseModel):
    title: str = "New Chat"
    folder_id: Optional[int] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    folder_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    title: str
    folder_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    folder_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 목록 조회 (폴더별 필터링 가능)"""
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    
    if folder_id is not None:
        query = query.filter(Conversation.folder_id == folder_id)
    
    conversations = query.order_by(Conversation.updated_at.desc()).all()
    return conversations


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 생성"""
    new_conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
        folder_id=conversation_data.folder_id
    )
    
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 상세 조회 (메시지 포함)"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 수정"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    if conversation_data.title is not None:
        conversation.title = conversation_data.title
    
    if conversation_data.folder_id is not None:
        conversation.folder_id = conversation_data.folder_id
    
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화 삭제"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    return None


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: int,
    role: str,
    content: str,
    sources: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대화에 메시지 추가"""
    # 대화 존재 확인
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # 메시지 생성
    new_message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources
    )
    
    db.add(new_message)
    
    # 대화 updated_at 갱신
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    return new_message
