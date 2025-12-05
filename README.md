# 궁디팡팡 AI 도슨트 (GDPP AI Docent)

**LG EXAONE 3.0 (7.8B) 기반 한국어 특화 RAG 챗봇 시스템** <br/>
로컬 LLM + Hybrid Retrieval로 구현한 캣페스타 전시 안내 서비스

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2.0-blue.svg)](https://react.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-0.13.0-orange.svg)](https://ollama.com/)
[![EXAONE](https://img.shields.io/badge/EXAONE-3.0--7.8B-purple.svg)](https://huggingface.co/LGAI-EXAONE)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)


## 프로젝트 개요

**궁디팡팡 AI 도슨트**는 (주)메쎄이상의 캣페스타 방문객을 위한 AI 기반 전시 안내 챗봇입니다. 

### 기획 의도 및 차별화

**기존 Llama 3.1 모델을 사용했으나, 국내 박람회(메쎄이상) 도메인의 특성상 한국어 뉘앙스와 정확한 안내가 중요하다고 판단하여 LG AI Research의 EXAONE 3.0 모델로 교체하여 성능을 최적화했습니다.**

- **완전한 로컬 시스템**: 외부 API 의존 없이 온프레미스 환경에서 구동 (비용 절감)
- **한국어 특화**: EXAONE 3.0으로 한국어 문맥 이해도 및 응답 품질 향상
- **RAG 기반 환각 방지**: 검색 증강 생성으로 정확한 정보만 제공
- **Hybrid Search**: Dense Vector + Sparse BM25로 고유명사(브랜드명) 검색 정확도 보완
- **One-Command 배포**: Docker Compose로 즉시 배포 가능

### 핵심 가치

| 구분 | 일반적인 챗봇 | 본 프로젝트 |
|------|--------------|------------|
| LLM | OpenAI API (유료) | EXAONE 3.0 (로컬, 무료) |
| 검색 | 단순 키워드 | Hybrid RAG (Vector + BM25) |
| 한국어 | 범용 모델 | 한국어 특화 모델 |
| 정확도 | 환각 발생 가능 | 환각 방지 시스템 |
| 배포 | 복잡한 설정 | Docker One-Command |

## 주요 기능

### 전시회 특화 도슨트 모드

**1. 브랜드 정보 제공**
- 243개 캣페스타 참가 브랜드 정보 검색
- 브랜드별 카테고리, 제품, 부스 위치 안내
- 홈페이지/SNS 링크 제공
- 사용자 질문에 맞는 브랜드 추천

**예시 질문:**
- "고양이 사료 추천해줘"
- "F구역에 어떤 브랜드가 있어?"
- "건강백서캣 부스 번호는?"

**2. 이벤트 정보 안내**
- 궁디팡팡 캣페스타 일정 및 장소
- 운영 시간 및 입장료 정보
- 사무국 연락처 및 FAQ

**3. 고양이 지식 제공**
- Wikipedia 기반 고양이 관련 지식 (12개 페이지)
- 품종, 행동, 건강, 영양 등 다양한 주제
- 신뢰할 수 있는 출처 기반 정보

**4. 응답 정확도 향상 시스템**
- **환각 방지**: 시스템 프롬프트 강화 + Temperature 0.3 설정
- **유사도 필터링**: 임계값 0.15 기반 관련성 낮은 문서 제거
- **출처 표시**: 모든 응답에 참고 자료 출처 명시
- **자연스러운 대화**: Context 반복 언급 제거

**5. 사용자 인증 및 관리**
- **비밀번호 강도 검증**: 실시간 5가지 조건 표시 (8자 이상, 대소문자, 숫자, 특수문자)
- **JWT 기반 인증**: 안전한 토큰 기반 인증
- **게스트 모드**: 로그인 없이 즉시 사용 가능
- **대화 히스토리**: 로그인 사용자 대화 자동 저장
- **관심 상품 관리**: URL 북마크 기능


## 시스템 아키텍처

### 1. 전체 시스템 구조
<img width="2268" height="1134" alt="슬라이드2" src="https://github.com/user-attachments/assets/dd167200-e135-4063-9801-c663bfcf26ef" />

### 2. 데이터 파이프라인 (RAG)
<img width="2268" height="1134" alt="슬라이드1" src="https://github.com/user-attachments/assets/ceca850a-b87d-4118-8f9c-28a69aa6edb0" />

### 데이터베이스 스키마 (SQLite)

```
┌─────────────────────────────────────────────────────────────┐
│                         users                               │
├─────────────────────────────────────────────────────────────┤
│ • id (PK)                                                   │
│ • email (UNIQUE)                                            │
│ • password_hash                                             │
│ • is_admin                                                  │
│ • created_at                                                │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┬─────────────┐
                ▼             ▼             ▼             ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     folders      │ │  conversations   │ │favorite_products │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ • id (PK)        │ │ • id (PK)        │ │ • id (PK)        │
│ • user_id (FK)   │ │ • user_id (FK)   │ │ • user_id (FK)   │
│ • name           │ │ • folder_id (FK) │ │ • title          │
│ • created_at     │ │ • title          │ │ • url            │
└──────────────────┘ │ • created_at     │ │ • created_at     │
                     │ • updated_at     │ │ • updated_at     │
                     └──────────────────┘ └──────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    messages      │
                     ├──────────────────┤
                     │ • id (PK)        │
                     │ • conversation_id│
                     │   (FK)           │
                     │ • role           │
                     │ • content        │
                     │ • sources (JSON) │
                     │ • created_at     │
                     └──────────────────┘
```

**관계:**
- `users` 1:N `folders`, `conversations`, `favorite_products`
- `folders` 1:N `conversations`
- `conversations` 1:N `messages`

### 데이터 플로우

1. **사용자 입력** → React UI에서 메시지 입력
2. **검색 단계** → FastAPI가 Hybrid Retriever로 관련 문서 검색
   - Dense Vector Search (의미 기반)
   - Sparse BM25 Search (키워드 기반)
   - 두 결과를 앙상블하여 최종 컨텍스트 생성
3. **생성 단계** → Ollama LLM이 컨텍스트 기반으로 응답 생성
   - 한국어 응답 생성
4. **응답 표시** → React UI에 출력 (출처 포함)
5. **대화 저장** → 로그인 사용자의 경우 SQLite에 저장



## 기술 스택

### Frontend
- **React 19**: 사용자 인터페이스 라이브러리
- **Vite 5**: 빌드 도구 및 개발 서버
- **Tailwind CSS 3**: 유틸리티 기반 CSS 프레임워크
- **Zustand**: 경량 상태 관리 라이브러리
- **Axios**: HTTP 클라이언트
- **React Router**: 클라이언트 사이드 라우팅

### Backend
- **Python 3.10**: 메인 프로그래밍 언어
- **FastAPI**: 백엔드 API 서버
- **Ollama**: 로컬 LLM 서빙

### Authentication & Database
- **SQLite**: 경량 관계형 데이터베이스
- **SQLAlchemy**: Python ORM
- **JWT (PyJWT)**: JSON Web Token 인증
- **bcrypt**: 비밀번호 해싱

### RAG System
- **Ko-SBERT** (`jhgan/ko-sbert-nli`): 한국어 임베딩 모델 (768차원)
- **ChromaDB**: 벡터 데이터베이스
- **BM25**: 키워드 기반 검색

### LLM
- **EXAONE 3.0 7.8B**: LG AI Research의 한국어 특화 LLM (4.8GB)
  - 2024년 8월 출시 최신 모델
  - 한국어 성능 최적화
  - 비상업적 연구/평가 목적 사용
- 로컬 CPU/GPU 가속 지원

### Data Collection
- **Wikipedia API**: 고양이 지식 수집
- **BeautifulSoup**: 웹 크롤링
- **Selenium**: 동적 콘텐츠 크롤링

### Development Tools
- **Conda**: 가상환경 관리
- **Git**: 버전 관리
- **WSL2**: 개발 환경 (Ubuntu on Windows)


## 기술적 의사결정 (Technical Decisions)

### 왜 EXAONE 3.0을 선택했는가?

**문제 상황:**
- 초기 Llama 3.1 8B 사용 시 한국어 응답 품질 저하
- Llama 3.2 3B로 경량화 시도 → 외국어(태국어 등) 혼입 발생
- 브랜드명, 부스 번호 등 정확한 정보 전달 필요

**해결:**
- **EXAONE 3.0 7.8B** (LG AI Research, 2024년 8월)
  - 한국어 문맥 이해도가 Llama 대비 우수
  - 외국어 혼입 제거, 자연스러운 한국어 응답
  - 국내 박람회 도메인에 최적화

**결과:**
- 부스 번호 검색 정확도 향상
- 외국어 혼입 제거
- 응답 품질 개선


### 왜 Hybrid Retrieval인가?

**문제 상황:**
- 단순 벡터 검색(Dense)만 사용 시 "애니몬다" 같은 고유명사 검색 실패
- 의미는 이해하지만 정확한 브랜드명 매칭 어려움

**해결:**
- **ChromaDB (Vector Search)** + **BM25 (Keyword Search)**
  - Vector Search: 의미 기반 검색 ("고양이 사료" → 관련 브랜드)
  - BM25: 키워드 정확 매칭 ("애니몬다" → Animonda 브랜드)
  - 앙상블 가중치: Vector 70% + BM25 30%

**결과:**
- 검색 정확도 향상
- 고유명사 검색 성공률 개선


### 왜 FastAPI + React + Docker인가?

**아키텍처 선택 이유:**

**1. FastAPI (Backend)**
- 비동기 처리로 LLM 응답 대기 시 다른 요청 처리 가능
- 자동 API 문서 생성 (`/docs`)
- Type Hints로 코드 안정성 확보

**2. React (Frontend)**
- 컴포넌트 기반 재사용성
- 실시간 채팅 UI에 최적화
- Zustand로 경량 상태 관리

**3. Docker Compose**
- 프론트/백/LLM 서버 통합 관리
- 환경 의존성 제거
- One-Command 배포 (`docker compose up`)

**결과:**
- MSA 고려한 프론트/백 분리
- 배포 환경 통일성 확보
- 개발/프로덕션 환경 일치


## 설치 및 실행

> **GCP/Docker 배포 가이드**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)를 참고하세요.

### Quick Start (Docker One-Command)

**가장 빠른 실행 방법 (5분):**

```bash
# 1. 저장소 클론
git clone https://github.com/newkimjiwon/GDPP-AI-Docent-LLM.git
cd GDPP-AI-Docent-LLM

# 2. Docker Compose 실행
docker compose up -d

# 3. EXAONE 3.0 모델 설치 (필수! 약 4.8GB, 5-10분 소요)
docker exec -it gdpp-ollama ollama pull anpigon/exaone-3.0-7.8b-instruct-llamafied

# 4. Vector DB 생성
docker exec -it gdpp-backend python src/rag/build_vectordb.py

# 5. 백엔드 재시작
docker compose restart backend

# 6. 접속
# - 프론트엔드: http://localhost:8000
# - 백엔드 API: http://localhost:8001
# - API 문서: http://localhost:8001/docs
```

**환경 변수 설정 (선택사항):**
```bash
# .env 파일 생성
echo "JWT_SECRET_KEY=your-super-secret-key-here" > .env
```


### 시스템 요구사항

**최소 사양:**
- CPU: 4코어 이상
- RAM: 16GB 이상
- 디스크: 30GB 이상 여유 공간
- OS: Linux (WSL2), macOS, Windows

**권장 사양:**
- CPU: 8코어 이상
- RAM: 32GB 이상
- GPU: NVIDIA GPU 8GB+ (RTX 3060 이상)
- 디스크: 50GB 이상

### 1. 환경 설정

```bash
# Conda 환경 생성
conda create -n gdpp python=3.10 -y
conda activate gdpp

# 프로젝트 클론
git clone <repository-url>
cd GDDPAIDocent

# 의존성 설치
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 JWT_SECRET_KEY 등을 수정하세요.
```

### 2. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Ollama 서비스 시작 (자동 시작됨)
# systemctl status ollama

# EXAONE 3.0 모델 다운로드 (약 4.8GB, 5-10분 소요)
ollama pull anpigon/exaone-3.0-7.8b-instruct-llamafied

# 모델 확인
ollama list
```

### 3. 벡터 데이터베이스 구축

```bash
# 프로젝트 루트에서
cd /path/to/GDDPAIDocent

# 벡터 DB 구축 (최초 1회만)
python src/rag/build_vectordb.py
```

**출력 예시:**
```
[INFO] 위키피디아 크롤링 시작 (12개 페이지)
[SUCCESS] 총 12개 페이지 크롤링 완료
[INFO] 64개 문서 임베딩 중...
[SUCCESS] 벡터 데이터베이스 구축 완료!
```

### 4. 서버 실행

**터미널 1: 백엔드 서버**
```bash
conda activate gdpp
cd /path/to/GDDPAIDocent
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2: React 프론트엔드**

#### 2.1 NVM (Node Version Manager) 설치 (최초 1회)

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

#### 2.2 Node.js 20 설치 및 활성화

```bash
# Node.js 20 LTS 버전 설치 (최초 1회)
nvm install 20

# Node.js 20 사용 설정
nvm use 20

# 기본 버전으로 설정 (선택사항)
nvm alias default 20

# 설치 확인
node --version  # v20.19.6 출력 확인
npm --version   # 10.8.2 출력 확인
```

#### 2.3 프론트엔드 의존성 설치 및 실행

```bash
# NVM 환경 로드 (새 터미널 세션마다 필요)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# React 앱 디렉토리로 이동
cd /path/to/GDDPAIDocent/frontend

# 의존성 설치 (최초 1회 또는 package.json 변경 시)
npm install

# 개발 서버 실행
npm run dev
```

**설치되는 주요 패키지:**
- `react` (19.0.0): UI 라이브러리
- `vite` (6.0.11): 빌드 도구 및 개발 서버
- `tailwindcss` (3.4.17): CSS 프레임워크
- `zustand` (5.0.2): 상태 관리
- `axios`: HTTP 클라이언트
- `react-router-dom`: 라우팅

**정상 실행 시 출력:**
```
  VITE v6.0.11  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

#### 2.4 프론트엔드 문제 해결

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


### 5. 접속

- **React 프론트엔드**: http://localhost:5173
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs



## 사용 방법

### 웹 UI 사용

1. **브라우저에서 접속**: http://localhost:5173
2. **게스트 모드로 시작**: 로그인 없이 바로 채팅 가능
3. **질문 입력**: 하단 입력창에 질문 입력
4. **로그인**: 대화를 저장하려면 "로그인하여 저장" 버튼 클릭
5. **회원가입**: 새 계정 만들기
6. **대화 관리**: 왼쪽 사이드바에서 대화 목록 확인
7. **상품 저장**: 오른쪽 패널에서 관심 상품 URL 저장

### 주요 기능

**게스트 모드**
- 로그인 없이 즉시 채팅 가능
- 대화 내용은 임시로만 저장 (새로고침 시 사라짐)

**로그인 사용자**
- 대화 히스토리 자동 저장
- 폴더로 대화 정리
- 대화 제목 수정
- 대화 삭제

**상품 URL 관리**
- 제목과 URL 함께 저장
- 저장된 상품 수정/삭제
- 클릭하여 새 탭에서 열기

### 예시 질문

**브랜드 정보:**
- "고양이 사료 추천해줘"
- "건강백서캣에 대해 알려줘"
- "F구역에 어떤 브랜드가 있어?"
- "고양이 간식 브랜드 알려줘"

**고양이 지식:**
- "고양이 품종은 어떤 것들이 있나요?"
- "페르시안 고양이에 대해 설명해줘"
- "고양이 건강 관리 방법은?"

### API 직접 호출

```bash
# 채팅 API
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "고양이 사료 추천해줘",
    "temperature": 0.7,
    "top_k": 5
  }'

# 시스템 상태 확인
curl "http://localhost:8000/api/status"
```



## 프로젝트 구조

```
GDDPAIDocent/
├── app/
│   └── frontend/                  # React 프론트엔드
├── data/
│   ├── raw/                       # 원본 데이터
│   │   ├── wikipedia_cat_knowledge.json
│   │   └── gdpp_brands.json
│   ├── processed/                 # 전처리된 데이터
│   │   └── all_chunks.json
│   └── vectordb/                  # ChromaDB 벡터 DB
├── src/
│   ├── api/                       # FastAPI 백엔드
│   │   ├── main.py
│   │   └── routes/
│   │       └── chat.py
│   ├── crawler/                   # 데이터 수집
│   │   ├── wikipedia_crawler.py
│   │   ├── gdpp_crawler.py
│   │   └── preprocessor.py
│   ├── model/                     # LLM 관련
│   │   ├── ollama_client.py
│   │   └── prompt_template.py
│   └── rag/                       # RAG 시스템
│       ├── embedder.py
│       ├── vector_store.py
│       ├── hybrid_retriever.py
│       └── build_vectordb.py
├── docs/                          # 문서
│   └── ollama_install_guide.md
├── requirements.txt               # Python 의존성
├── .env.example                   # 환경 변수 템플릿
├── PROGRESS.md                    # 진행 상황
├── RUN_GUIDE.md                   # 실행 가이드
└── README.md                      # 프로젝트 문서 (본 파일)
```



## 데이터 현황

### 수집된 데이터

| 데이터 소스 | 항목 수 | 총 크기 | 설명 |
| :--- | :--- | :--- | :--- |
| Wikipedia | 12 페이지 | 36,911자 | 고양이 관련 지식 (품종, 행동, 건강, 영양 등) |
| GDPP 브랜드 | 243개 | 297,010자 | 캣페스타 참가 브랜드 정보 |
| GDPP 이벤트 | 1개 | 1,139자 | 2025년 일정, 장소, 운영시간, 연락처 |
| GDPP FAQ | 39개 | 14,653자 | 자주 묻는 질문 및 답변 |
| **총 청크** | **297개** | **100,907자** | **전처리 완료** |


### 브랜드 카테고리 분포

- **사료/간식**: 15개 브랜드
- **용품**: 18개 브랜드
- **헬스케어**: 6개 브랜드
- **아트/기타**: 13개 브랜드

### 벡터 DB 통계

- **임베딩 모델**: Ko-SBERT (768차원)
- **총 벡터 수**: 64개
- **평균 청크 길이**: 487자
- **검색 방식**: Hybrid (Vector 70% + BM25 30%)



## 개발 과정

### Phase 1: 환경 설정 및 프로젝트 구조
- Python 3.10 가상환경 설정
- 프로젝트 디렉토리 구조 생성
- 의존성 관리 (`requirements.txt`)

### Phase 2: 데이터 엔지니어링
- Wikipedia API로 고양이 지식 수집
- GDPP 브랜드 데이터 구조화 (수동 수집)
- Semantic Chunking으로 데이터 분할
- 메타데이터 추출 (출처, 카테고리, URL 등)

### Phase 3: RAG 시스템 구축
- Ko-SBERT 임베딩 모델 설정
- ChromaDB 벡터 데이터베이스 구축
- Hybrid Search 구현 (Dense + Sparse)
- 검색 성능 검증

### Phase 4: 로컬 LLM 서빙
- Ollama 설치 및 설정
- Llama 3.1:8b 모델 다운로드
- Prompt Engineering (시스템 프롬프트, 컨텍스트 주입)
- LLM 응답 생성 테스트

### Phase 5: 백엔드 API 개발
- FastAPI 프로젝트 초기화
- `/api/chat` 엔드포인트 구현
- RAG 시스템 통합
- 에러 핸들링 및 로깅

### Phase 6: 프론트엔드 개발
- React 챗봇 UI 구현
- 실시간 대화 인터페이스
- 추천 질문 기능
- 출처 표시 기능



## 성능 및 최적화

### LLM 응답 속도 및 리소스 (Benchmark)
실제 배포 환경에서 측정한 EXAONE 3.0 (7.8B) 모델의 성능 지표입니다.

| 환경 | 하드웨어 스펙 | 평균 응답 시간 | 토큰 생성 속도 | 비고 |
|:---:|:---:|:---:|:---:|:---|
| **Local / GPU** | NVIDIA RTX 3090 (24GB) | **5 ~ 10초** | ~50 tokens/sec | **권장 사양 (쾌적함)** |
| **Cloud / CPU** | GCP e2-standard-8 (8 vCPU) | 60 ~ 90초 | ~5-10 tokens/sec | 최소 사양 (실행 가능) |

### 성능 분석
- **GPU 가속 권장**: 7.8B 모델의 특성상 CPU 환경에서는 연산 지연이 발생하므로, 실시간 서비스 시 **GPU 환경을 강력히 권장**합니다.
- **메모리 최적화**: 모델(약 4.8GB)과 벡터 DB, 애플리케이션을 포함하여 **총 약 8GB의 메모리**를 점유하여, 16GB RAM 환경에서도 안정적으로 구동됩니다.
- **검색 속도 (RAG)**: Hybrid Search(BM25+Vector) 단계는 **평균 0.1초 미만**으로 병목 없이 매우 빠르게 수행됩니다.

### 정확도 개선
- **환각 방지**: 
  - 시스템 프롬프트 강화
  - Temperature 0.7 → 0.3 감소
  - Context 반복 언급 제거
- **유사도 필터링**: 
  - 임계값 0.15 적용
  - 평균 5개 → 1-3개 고품질 문서 선별
- **한국어 품질**: 
  - EXAONE 3.0 사용으로 외국어 혼입 제거
  - 자연스러운 한국어 응답

### 최적화 기법
- **임베딩 캐싱**: 동일 쿼리 재사용
- **배치 처리**: 벡터 DB 구축 시 배치 크기 32
- **프롬프트 최적화**: 컨텍스트 길이 제한 (512 토큰)
- **Ollama 최적화**: 
  - `OLLAMA_KEEP_ALIVE=-1` (모델 영구 유지)
  - `OLLAMA_NUM_PARALLEL=4` (병렬 처리)


## 개발자

- **개발자**: 김지원
- **프로젝트 기간**: 2025.11.28 - 2025.12.05
- **제출**: (주)메쎄이상 웹 & AI 개발 부문 채용 과제
- **GitHub**: [https://github.com/newkimjiwon/GDPP-AI-Docent-LLM](https://github.com/newkimjiwon/GDPP-AI-Docent-LLM)
- **이메일**: newkimjiwon@gmail.com