# File: src/auth/jwt.py
"""
JWT 토큰 유틸리티
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

import os
from dotenv import load_dotenv

load_dotenv()

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    print(f"[DEBUG] Creating token with SECRET_KEY: {SECRET_KEY[:10]}...")
    print(f"[DEBUG] Token data: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증"""
    try:
        print(f"[DEBUG] Verifying token with SECRET_KEY: {SECRET_KEY[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"[DEBUG] JWT verification error: {e}")
        return None
