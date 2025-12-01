# File: src/api/routes/auth.py
"""
인증 API 라우트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.database.db import get_db
from src.models.user import User
from src.auth import hash_password, verify_password, create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()


# Pydantic 스키마
class UserRegister(BaseModel):
    email: str
    password: str
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식 검증"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        비밀번호 강도 검증
        - 최소 8자 이상
        - 대문자 1개 이상
        - 소문자 1개 이상
        - 숫자 1개 이상
        """
        if len(password) < 8:
            return False, "비밀번호는 최소 8자 이상이어야 합니다"
        
        if not any(c.isupper() for c in password):
            return False, "비밀번호에 대문자가 최소 1개 포함되어야 합니다"
        
        if not any(c.islower() for c in password):
            return False, "비밀번호에 소문자가 최소 1개 포함되어야 합니다"
        
        if not any(c.isdigit() for c in password):
            return False, "비밀번호에 숫자가 최소 1개 포함되어야 합니다"
        
        return True, "유효한 비밀번호입니다"


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


# 현재 사용자 가져오기 (의존성)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """JWT 토큰에서 현재 사용자 가져오기"""
    token = credentials.credentials
    print(f"[DEBUG] Received token: {token[:20]}...")  # 토큰 앞부분만 출력
    
    payload = verify_token(token)
    print(f"[DEBUG] Token payload: {payload}")
    
    if payload is None:
        print("[DEBUG] Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id_str = payload.get("sub")
    print(f"[DEBUG] User ID from token (string): {user_id_str}")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"[DEBUG] User not found in database: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    print(f"[DEBUG] User authenticated: {user.email}")
    return user


# 관리자 권한 확인 (의존성)
async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """관리자 권한 확인"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """회원가입"""
    # 이메일 형식 검증
    if not UserRegister.validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 이메일 형식입니다"
        )
    
    # 비밀번호 강도 검증
    is_valid, message = UserRegister.validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 비밀번호 해싱
    hashed_password = hash_password(user_data.password)
    
    # 사용자 생성
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """로그인"""
    # 사용자 조회
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 비밀번호 검증
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 사용자 정보"""
    return current_user
