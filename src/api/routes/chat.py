# File: src/api/routes/chat.py
"""
챗봇 API 라우트
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.rag.embedder import KoSBERTEmbedder
from src.rag.vector_store import VectorStore
from src.rag.hybrid_retriever import HybridRetriever
from src.model.ollama_client import OllamaClient
from src.model.prompt_template import create_chat_prompt
from src.database.db import get_db
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.user import User
from src.api.routes.auth import get_current_user_optional


router = APIRouter()

# 전역 변수로 초기화 (앱 시작 시 한 번만)
embedder = None
vector_store = None
retriever = None
ollama_client = None


def initialize_components():
    """컴포넌트 초기화"""
    global embedder, vector_store, retriever, ollama_client
    
    if embedder is None:
        print("[INFO] 임베더 초기화 중...")
        embedder = KoSBERTEmbedder()
    
    if vector_store is None:
        print("[INFO] 벡터 스토어 초기화 중...")
        vector_store = VectorStore(
            persist_directory="./data/vectordb",
            collection_name="gdpp_knowledge"
        )
    
    if retriever is None:
        print("[INFO] 하이브리드 검색기 초기화 중...")
        retriever = HybridRetriever(
            vector_store=vector_store,
            embedder=embedder
        )
    
    if ollama_client is None:
        print("[INFO] Ollama 클라이언트 초기화 중...")
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"[INFO] Ollama URL: {ollama_base_url}")
        ollama_client = OllamaClient(
            base_url=ollama_base_url,
            model="anpigon/exaone-3.0-7.8b-instruct-llamafied"  # EXAONE 3.0 for Korean
        )


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    conversation_id: Optional[int] = None  # 로그인 사용자의 대화 ID
    temperature: Optional[float] = 0.3  # 낮은 temperature로 환각 방지
    max_tokens: Optional[int] = 2048
    top_k: Optional[int] = 5


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str
    sources: list


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    챗봇 엔드포인트 (비스트리밍)
    
    Args:
        request: 채팅 요청
        current_user: 현재 사용자 (선택적)
        db: 데이터베이스 세션
        
    Returns:
        ChatResponse: 챗봇 응답
    """
    try:
        # 컴포넌트 초기화
        initialize_components()
        
        # 1. 하이브리드 검색
        print(f"[INFO] 검색 쿼리: {request.message}")
        search_results = retriever.hybrid_search(
            query=request.message,
            k=request.top_k
        )
        
        # 1.5. 유사도 필터링 (낮은 점수 문서 제외)
        SIMILARITY_THRESHOLD = 0.15  # 하이브리드 점수 임계값 (0.15로 조정)
        filtered_results = [
            r for r in search_results 
            if r.get('hybrid_score', 0) >= SIMILARITY_THRESHOLD
        ]
        
        # 필터링 결과 로그
        print(f"[INFO] 검색 결과: {len(search_results)}개 → 필터링 후: {len(filtered_results)}개")
        if filtered_results:
            print(f"[INFO] 최고 점수: {filtered_results[0].get('hybrid_score', 0):.4f}")
            print(f"[INFO] 최저 점수: {filtered_results[-1].get('hybrid_score', 0):.4f}")
        
        # 필터링된 결과가 없으면 최소 1개는 사용
        if not filtered_results and search_results:
            print("[WARNING] 필터링 결과 없음, 최상위 1개 문서 사용")
            filtered_results = search_results[:1]
        
        # 2. 프롬프트 생성 (필터링된 결과 사용)
        prompt_data = create_chat_prompt(request.message, filtered_results)
        
        # 3. LLM 호출
        print("[INFO] LLM 호출 중...")
        response = ollama_client.generate(
            prompt=prompt_data['prompt'],
            system=prompt_data['system'],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 4. 소스 정보 추출 (필터링된 결과 사용)
        sources = []
        for result in filtered_results[:3]:  # 상위 3개만
            metadata = result['metadata']
            sources.append({
                "source": metadata.get('source', ''),
                "title": metadata.get('brand_name') or metadata.get('title', ''),
                "score": result.get('hybrid_score', 0)
            })
        
        # 5. 로그인 사용자의 경우 메시지 저장
        if current_user and request.conversation_id:
            print(f"[INFO] 메시지 저장 중... (conversation_id: {request.conversation_id})")
            
            # 대화 존재 확인
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            
            if conversation:
                # 사용자 메시지 저장
                user_message = Message(
                    conversation_id=request.conversation_id,
                    role="user",
                    content=request.message,
                    sources=None
                )
                db.add(user_message)
                
                # AI 응답 저장
                assistant_message = Message(
                    conversation_id=request.conversation_id,
                    role="assistant",
                    content=response,
                    sources={"sources": sources}
                )
                db.add(assistant_message)
                
                # 대화 updated_at 갱신
                conversation.updated_at = datetime.utcnow()
                
                db.commit()
                print("[INFO] 메시지 저장 완료")
            else:
                print(f"[WARNING] 대화를 찾을 수 없음: {request.conversation_id}")
        
        return ChatResponse(
            response=response,
            sources=sources
        )
        
    except Exception as e:
        import traceback
        print(f"[ERROR] {str(e)}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    챗봇 엔드포인트 (스트리밍)
    
    Args:
        request: 채팅 요청
        
    Returns:
        StreamingResponse: 스트리밍 응답
    """
    try:
        # 컴포넌트 초기화
        initialize_components()
        
        # 1. 하이브리드 검색
        print(f"[INFO] 검색 쿼리: {request.message}")
        search_results = retriever.hybrid_search(
            query=request.message,
            k=request.top_k
        )
        
        # 2. 프롬프트 생성
        prompt_data = create_chat_prompt(request.message, search_results)
        
        # 3. 스트리밍 생성기
        async def generate():
            # 먼저 소스 정보 전송
            sources = []
            for result in search_results[:3]:
                metadata = result['metadata']
                sources.append({
                    "source": metadata.get('source', ''),
                    "title": metadata.get('brand_name') or metadata.get('title', ''),
                    "score": result.get('hybrid_score', 0)
                })
            
            yield f"data: {{'type': 'sources', 'data': {sources}}}\n\n"
            
            # LLM 응답 스트리밍
            for chunk in ollama_client.generate_stream(
                prompt=prompt_data['prompt'],
                system=prompt_data['system'],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield f"data: {{'type': 'token', 'data': '{chunk}'}}\n\n"
            
            # 완료 신호
            yield "data: {'type': 'done'}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def status():
    """시스템 상태 확인"""
    initialize_components()
    
    # Ollama 연결 확인
    ollama_status = ollama_client.check_connection()
    
    # 벡터 DB 통계
    db_stats = vector_store.get_collection_stats()
    
    return {
        "ollama": {
            "connected": ollama_status,
            "model": ollama_client.model
        },
        "vector_db": {
            "collection": db_stats['collection_name'],
            "document_count": db_stats['document_count']
        },
        "components": {
            "embedder": embedder is not None,
            "retriever": retriever is not None
        }
    }
