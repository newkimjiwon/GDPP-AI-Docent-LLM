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

# EXAONE 3.0 모델 다운로드 (약 4.8GB, 5-10분 소요)
ollama pull anpigon/exaone-3.0-7.8b-instruct-llamafied
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

#### 4.1 NVM (Node Version Manager) 설치 (최초 1회)

NVM이 설치되어 있지 않다면 먼저 설치합니다:

```bash
# NVM 설치 스크립트 다운로드 및 실행
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 셸 설정 파일에 NVM 환경 변수 추가
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# 설정 적용
source ~/.bashrc  # bash 사용 시
# 또는
source ~/.zshrc   # zsh 사용 시

# NVM 설치 확인
nvm --version
```

#### 4.2 Node.js 20 설치 및 활성화

```bash
# Node.js 20 LTS 버전 설치 (최초 1회)
nvm install 20

# Node.js 20 사용 설정
nvm use 20

# 기본 버전으로 설정 (선택사항 - 새 터미널에서 자동 활성화)
nvm alias default 20

# 설치 확인
node --version  # v20.19.6 출력 확인
npm --version   # 10.8.2 출력 확인
```

#### 4.3 프론트엔드 의존성 설치

새 터미널에서 실행할 때마다 NVM 환경을 먼저 로드해야 합니다:

```bash
# NVM 환경 로드 (새 터미널 세션마다 필요)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# 프론트엔드 디렉토리로 이동
cd /mnt/d/Project/GDDPAIDocent/frontend

# 의존성 설치 (최초 1회 또는 package.json 변경 시)
npm install
```

**설치되는 주요 패키지:**
- `react` (19.0.0): UI 라이브러리
- `vite` (6.0.11): 빌드 도구 및 개발 서버
- `tailwindcss` (3.4.17): CSS 프레임워크
- `zustand` (5.0.2): 상태 관리
- `axios`: HTTP 클라이언트
- `react-router-dom`: 라우팅

**설치 시간:** 약 1-3분 소요 (인터넷 속도에 따라 다름)

#### 4.4 개발 서버 실행

```bash
# Vite 개발 서버 시작
npm run dev
```

**정상 실행 시 출력:**
```
  VITE v6.0.11  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

React 앱이 실행됩니다: http://localhost:5173

#### 4.5 프론트엔드 환경 변수 설정

프론트엔드는 `.env.production` 파일에서 API 엔드포인트를 읽습니다:

```bash
# frontend/.env.production
VITE_API_BASE_URL=/api
```

**개발 환경에서 백엔드 연결:**
- 로컬 백엔드 (포트 8000): `http://localhost:8000/api`
- Docker 백엔드 (포트 8001): `http://localhost:8001/api`

#### 4.6 프론트엔드 문제 해결

**문제: `vite: not found` 오류**
```bash
# 원인: node_modules가 설치되지 않았거나 손상됨
# 해결:
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**문제: 포트 5173이 이미 사용 중**
```bash
# 해결: 다른 포트로 실행
npm run dev -- --port 5174
```

**문제: NVM 명령어를 찾을 수 없음**
```bash
# 원인: NVM 환경 변수가 로드되지 않음
# 해결: 매번 새 터미널에서 다음 명령 실행
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20
```

**문제: API 연결 실패 (Network Error)**
- 백엔드 서버가 실행 중인지 확인: http://localhost:8000/docs
- 브라우저 콘솔(F12)에서 네트워크 탭 확인
- CORS 오류인 경우 백엔드 CORS 설정 확인


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

### 느린 응답 속도

- GPU 사용 권장
- 더 작은 모델 사용 가능 (성능 저하 가능성)
- 다른 GPU 프로세스 종료

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

- Wikipedia 고양이 지식: 12개 페이지 (36,911자)
- GDPP 브랜드: 243개 (297,010자)
- GDPP 이벤트 정보: 1개 (1,139자)
- GDPP FAQ: 39개 (14,653자)
- 총 청크: 297개 (전처리 완료)
- 임베딩 차원: 768 (Ko-SBERT)


## 성능

- 검색 속도: ~100ms
- LLM 응답 속도: ~2-5초 (GPU 사용 시)
- 메모리 사용량: ~8GB (모델 + 벡터 DB)
