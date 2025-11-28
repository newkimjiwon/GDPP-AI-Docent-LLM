# File: src/api/main.py
"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat

# FastAPI 앱 생성
app = FastAPI(
    title="GDPP AI Docent API",
    description="궁디팡팡 캣페스타 AI 도슨트 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "GDPP AI Docent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
