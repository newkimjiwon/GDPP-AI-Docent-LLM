# File: src/api/routes/admin.py
"""
관리자 전용 API 라우트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.database.db import get_db
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.api.routes.auth import get_current_admin_user


router = APIRouter()


# Response 스키마
class UserStats(BaseModel):
    id: int
    email: str
    is_admin: bool
    created_at: datetime
    conversation_count: int
    
    class Config:
        from_attributes = True


class ConversationStats(BaseModel):
    id: int
    user_id: int
    user_email: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    total_users: int
    total_conversations: int
    total_messages: int
    admin_users: int
    users_today: int
    conversations_today: int


@router.get("/users", response_model=List[UserStats])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """모든 사용자 목록 조회 (관리자 전용)"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        conversation_count = db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).count()
        
        result.append(UserStats(
            id=user.id,
            email=user.email,
            is_admin=user.is_admin,
            created_at=user.created_at,
            conversation_count=conversation_count
        ))
    
    return result


@router.get("/conversations", response_model=List[ConversationStats])
async def get_all_conversations(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """모든 대화 목록 조회 (관리자 전용)"""
    conversations = db.query(Conversation).offset(skip).limit(limit).all()
    
    result = []
    for conv in conversations:
        user = db.query(User).filter(User.id == conv.user_id).first()
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        result.append(ConversationStats(
            id=conv.id,
            user_id=conv.user_id,
            user_email=user.email if user else "Unknown",
            title=conv.title,
            message_count=message_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))
    
    return result


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """시스템 통계 조회 (관리자 전용)"""
    # 총 사용자 수
    total_users = db.query(User).count()
    
    # 총 대화 수
    total_conversations = db.query(Conversation).count()
    
    # 총 메시지 수
    total_messages = db.query(Message).count()
    
    # 관리자 수
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    # 오늘 가입한 사용자 수
    today = datetime.utcnow().date()
    users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    # 오늘 생성된 대화 수
    conversations_today = db.query(Conversation).filter(
        func.date(Conversation.created_at) == today
    ).count()
    
    return SystemStats(
        total_users=total_users,
        total_conversations=total_conversations,
        total_messages=total_messages,
        admin_users=admin_users,
        users_today=users_today,
        conversations_today=conversations_today
    )


@router.get("/users/{user_id}/conversations", response_model=List[ConversationStats])
async def get_user_conversations(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """특정 사용자의 대화 목록 조회 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        result.append(ConversationStats(
            id=conv.id,
            user_id=conv.user_id,
            user_email=user.email,
            title=conv.title,
            message_count=message_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))
    
    return result
