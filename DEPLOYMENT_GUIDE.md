# GDPP AI Docent - 배포 가이드 (GCP/Docker)

이 가이드는 Google Cloud Platform (GCP) Compute Engine 환경에서 Docker Compose를 사용하여 프로젝트를 배포하는 방법을 설명합니다.

## 1. 사전 요구사항

- **GCP 인스턴스**: e2-standard-4 (4 vCPU, 16GB RAM) 이상 권장
- **OS**: Ubuntu 20.04 LTS 이상
- **Docker & Docker Compose**: 설치 필요
- **Git**: 설치 필요

## 2. 설치 및 설정

### 2.1 프로젝트 클론
```bash
git clone https://github.com/newkimjiwon/GDPP-AI-Docent-LLM.git
cd GDPP-AI-Docent-LLM
```

### 2.2 환경 변수 설정
`.env.production` 파일을 생성하거나 수정합니다.
```bash
# .env.production 예시
VITE_API_BASE_URL=/api
JWT_SECRET_KEY=your_secret_key_here
```

## 3. 배포 (Docker Compose)

CPU 환경에 최적화된 설정으로 배포합니다.

### 3.1 Docker 컨테이너 빌드 및 실행

```bash
# 최신 코드 가져오기
git pull origin test-gcp  # 또는 main

# Docker 컨테이너 빌드 및 실행
sudo docker compose up -d --build
```

**실행 결과 확인:**
```bash
sudo docker compose ps
```

정상적으로 실행되면 다음 3개의 컨테이너가 실행 중이어야 합니다:
- `gdpp-frontend` (Nginx + React)
- `gdpp-backend` (FastAPI)
- `gdpp-ollama` (Ollama LLM 서버)

### 3.2 EXAONE 3.0 모델 설치 (필수!)

Docker 컨테이너가 실행된 후, Ollama 컨테이너 내부에서 모델을 다운로드해야 합니다.

```bash
# Ollama 컨테이너에서 EXAONE 3.0 모델 다운로드 (약 4.8GB, 5-10분 소요)
sudo docker exec -it gdpp-ollama ollama pull anpigon/exaone-3.0-7.8b-instruct-llamafied
```

**다운로드 진행 상황:**
```
pulling manifest
pulling 8934d96d3f08... 100% ▕████████████████▏ 4.8 GB
pulling 8c17c2ebb0ea... 100% ▕████████████████▏ 7.0 KB
pulling 7c23fb36d801... 100% ▕████████████████▏ 4.8 KB
pulling 2e0493f67d0c... 100% ▕████████████████▏   59 B
pulling fa8235e5b48f... 100% ▕████████████████▏  491 B
verifying sha256 digest
writing manifest
success
```

**모델 설치 확인:**
```bash
sudo docker exec -it gdpp-ollama ollama list
```

출력 예시:
```
NAME                                           ID              SIZE      MODIFIED
anpigon/exaone-3.0-7.8b-instruct-llamafied     abc123def456    4.8 GB    2 minutes ago
```

### 3.3 벡터 데이터베이스 생성 (필수!)

모델 설치가 완료되면, 백엔드 컨테이너에서 벡터 DB를 구축합니다.

```bash
# 백엔드 컨테이너에서 벡터 DB 생성 스크립트 실행
sudo docker exec -it gdpp-backend python src/rag/build_vectordb.py
```

**벡터 DB 생성 진행 상황:**
```
[INFO] 데이터 파일 로드 중...
[INFO] Wikipedia: 12개 페이지
[INFO] GDPP 브랜드: 243개
[INFO] GDPP 이벤트: 1개
[INFO] GDPP FAQ: 39개
[INFO] 총 297개 청크 생성
[INFO] Ko-SBERT 임베딩 모델 로드 중...
[INFO] 벡터 임베딩 생성 중... (297개 문서)
[INFO] ChromaDB에 저장 중...
[SUCCESS] 벡터 데이터베이스 구축 완료!
[INFO] 저장 경로: /app/data/vectordb
```

### 3.4 백엔드 서비스 재시작

벡터 DB 생성이 완료되면 백엔드를 재시작하여 변경사항을 반영합니다.

```bash
# 백엔드 컨테이너 재시작
sudo docker compose restart backend
```

### 3.5 배포 완료 확인

모든 서비스가 정상적으로 실행되는지 확인합니다.

```bash
# 로그 확인
sudo docker compose logs -f

# 특정 서비스 로그만 확인
sudo docker compose logs -f backend
```

**접속 테스트:**
- 프론트엔드: http://your-server-ip:8000
- 백엔드 API: http://your-server-ip:8001
- API 문서: http://your-server-ip:8001/docs

### 주요 설정 (`docker-compose.yml`)
- **OLLAMA_NUM_PARALLEL=4**: 최대 4명 동시 접속 처리
- **OLLAMA_KEEP_ALIVE=-1**: 모델을 메모리에 영구 상주 (Cold Start 방지)
- **OLLAMA_MAX_LOADED_MODELS=1**: 메모리 절약을 위해 1개 모델만 로드

## 4. 트러블슈팅

### 4.1 응답 속도가 느림
- **원인**: CPU 전용 인스턴스에서는 LLM 추론 속도가 느릴 수 있습니다.
- **해결**: 
    - 첫 질문은 모델 로딩으로 인해 30초~1분 소요될 수 있습니다.
    - 두 번째 질문부터는 `KEEP_ALIVE` 설정 덕분에 조금 더 빨라집니다.
    - 더 빠른 속도를 원한다면 `phi3` 또는 `gemma2:2b` 같은 경량 모델로 변경을 고려하세요.

### 4.2 504 Gateway Timeout
- **원인**: Nginx 또는 백엔드 타임아웃 설정보다 처리가 오래 걸림.
- **해결**: 현재 설정은 600초(10분)로 넉넉하게 잡혀 있습니다. 만약 이보다 더 오래 걸린다면 인스턴스 사양을 높여야 합니다.

### 4.3 404 Not Found (API)
- **원인**: API 주소 설정 오류.
- **해결**: 프론트엔드에서 `/api` 접두사가 이중으로 붙지 않는지 확인하세요. (`/api/api/chat` -> `/api/chat`)

## 5. 프론트엔드 개발 환경 설정

Docker 없이 프론트엔드만 로컬에서 개발하려면 다음 단계를 따르세요.

### 5.1 NVM (Node Version Manager) 설치

```bash
# NVM 설치 스크립트 다운로드 및 실행
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 셸 설정 파일에 NVM 환경 변수 추가
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# 설정 적용 (또는 터미널 재시작)
source ~/.bashrc  # 또는 source ~/.zshrc
```

### 5.2 Node.js 20 설치 및 활성화

```bash
# Node.js 20 LTS 버전 설치
nvm install 20

# Node.js 20 사용 설정
nvm use 20

# 기본 버전으로 설정 (선택사항)
nvm alias default 20

# 설치 확인
node --version  # v20.x.x 출력 확인
npm --version   # 10.x.x 출력 확인
```

### 5.3 프론트엔드 의존성 설치

```bash
# 프론트엔드 디렉토리로 이동
cd /mnt/d/Project/GDPP-AI-Docent-LLM/frontend

# package.json의 모든 의존성 설치
# 이 명령은 node_modules 폴더를 생성하고 필요한 패키지를 다운로드합니다
npm install
```

**설치되는 주요 패키지:**
- `react` (19.0.0): UI 라이브러리
- `vite` (6.0.11): 빌드 도구 및 개발 서버
- `tailwindcss` (3.4.17): CSS 프레임워크
- `zustand` (5.0.2): 상태 관리
- `axios`: HTTP 클라이언트
- `react-router-dom`: 라우팅

### 5.4 개발 서버 실행

```bash
# 새 터미널 세션에서는 항상 NVM 환경을 먼저 로드해야 합니다
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# Vite 개발 서버 시작
npm run dev
```

**개발 서버 실행 결과:**
```
  VITE v6.0.11  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

브라우저에서 http://localhost:5173 접속

### 5.5 프론트엔드 환경 변수 설정

`.env.production` 파일에서 API 엔드포인트를 설정합니다:

```bash
# frontend/.env.production
VITE_API_BASE_URL=/api
```

**개발 환경에서 백엔드 연결:**
- Docker로 백엔드 실행 시: `http://localhost:8001/api`
- 로컬 백엔드 실행 시: `http://localhost:8000/api`

### 5.6 프로덕션 빌드 (배포용)

```bash
# 프로덕션 빌드 생성
npm run build

# 빌드 결과물은 dist/ 폴더에 생성됩니다
# Docker 이미지 빌드 시 자동으로 사용됩니다
```

### 5.7 프론트엔드 문제 해결

**문제: `vite: not found` 오류**
```bash
# 해결: node_modules가 없거나 손상된 경우
rm -rf node_modules package-lock.json
npm install
```

**문제: 포트 5173이 이미 사용 중**
```bash
# 해결: 다른 포트로 실행
npm run dev -- --port 5174
```

**문제: API 연결 실패 (CORS 오류)**
- 백엔드 서버가 실행 중인지 확인
- `VITE_API_BASE_URL` 환경 변수 확인
- 브라우저 콘솔에서 네트워크 탭 확인

## 6. 주요 명령어

### Docker 관련
```bash
# 로그 확인 (실시간)
sudo docker compose logs -f

# 백엔드 로그만 확인
sudo docker compose logs -f backend

# 프론트엔드 로그만 확인
sudo docker compose logs -f frontend

# 컨테이너 상태 확인
sudo docker compose ps

# 서비스 중지
sudo docker compose down

# 서비스 재시작 (코드 변경 후)
sudo docker compose restart backend
sudo docker compose restart frontend
```

### 프론트엔드 개발 (로컬)
```bash
# NVM 환경 로드 (새 터미널마다 필요)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# 개발 서버 실행
cd /mnt/d/Project/GDPP-AI-Docent-LLM/frontend
npm run dev

# 의존성 재설치
npm install

# 프로덕션 빌드
npm run build
```
