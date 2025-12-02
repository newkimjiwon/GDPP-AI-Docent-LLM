# GDPP AI Docent - 실행 가이드

## 시스템 요구사항
- Python 3.10
- RTX 3090 24GB (CUDA 11.8)
- Ollama 설치

## 설치 및 실행

> **서버 배포 (Docker)**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)를 참고하세요.

### 1. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# Ollama 서비스 시작
ollama serve

# 새 터미널에서 모델 다운로드 (약 4.9GB)
ollama pull llama3.1:8b
```

### 2. Python 환경 설정

```bash
# conda 환경 활성화
conda activate gdpp

# 의존성 설치 (이미 설치됨)
pip install -r requirements.txt
```

### 3. 백엔드 서버 실행

```bash
# 프로젝트 루트에서
cd /mnt/d/Project/GDDPAIDocent

# FastAPI 서버 시작
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면: http://localhost:8000

### 4. React 프론트엔드 실행

새 터미널에서:

```bash
# Node.js 20 환경 설정 (nvm 사용)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# React 앱 실행
cd /mnt/d/Project/GDDPAIDocent/frontend
npm run dev
```

React 앱이 실행됩니다: http://localhost:5173

**React 프론트엔드 기능**
- 게스트 모드: 로그인 없이 바로 채팅 가능
- 로그인/회원가입: 대화 히스토리 저장
- 대화 관리: 폴더로 대화 정리
- 상품 URL 저장: 오른쪽 패널에서 관심 상품 URL 보관
- ChatGPT 스타일 UI: 현대적이고 직관적인 인터페이스


## 사용 방법

1. **게스트로 시작**: 로그인 없이 바로 채팅 가능
2. **질문 입력**: 메시지 입력창에 질문 입력
3. **로그인**: 대화를 저장하려면 "로그인하여 저장" 버튼 클릭
4. **상품 저장**: 오른쪽 패널에서 관심 상품 URL 저장

## 예시 질문

- "고양이 사료 추천해줘"
- "건강백서캣에 대해 알려줘"
- "고양이 품종은 어떤 것들이 있나요?"
- "고양이 간식 브랜드 알려줘"
- "부스 위치 알려줘"

## 문제 해결

### Ollama 연결 실패
```bash
# Ollama 서비스 확인
ollama list

# Ollama 재시작
pkill ollama
ollama serve
```

### API 서버 연결 실패
- 백엔드 서버가 실행 중인지 확인
- 포트 8000이 사용 가능한지 확인

### GPU 메모리 부족
- 더 작은 모델 사용: `ollama pull llama3.2:3b`
- 다른 GPU 프로세스 종료

## 아키텍처

```
[User] → [React UI] → [FastAPI Backend] → [RAG System]
                                                    ↓
                                            [Hybrid Retriever]
                                                    ↓
                                    [Vector DB (ChromaDB) + BM25]
                                                    ↓
                                            [Ollama LLM]
```

## 데이터 현황

- Wikipedia 고양이 지식: 12개 페이지
- GDPP 브랜드: 52개
- 총 청크: 64개
- 임베딩 차원: 768 (Ko-SBERT)

## 성능

- 검색 속도: ~100ms
- LLM 응답 속도: ~2-5초 (GPU 사용 시)
- 메모리 사용량: ~8GB (모델 + 벡터 DB)
