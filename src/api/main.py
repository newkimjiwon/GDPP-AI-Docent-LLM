# File: src/api/main.py
"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, auth, folders, conversations
from src.database.db import init_db

# FastAPI 앱 생성
app = FastAPI(
    title="GDPP AI Docent API",
    description="궁디팡팡 캣페스타 AI 도슨트 API",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터베이스 초기화"""
    init_db()
    print("[INFO] 데이터베이스 초기화 완료")

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(folders.router, prefix="/api/folders", tags=["folders"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# 관심상품 라우터 추가
from .routes import favorites
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])

# 관리자 라우터 추가
from .routes import admin
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "GDPP AI Docent API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
