# GDPP AI Docent - macOS 실행 가이드

> macOS (Apple Silicon M3) 환경에서 궁디팡팡 AI 도슨트 실행하기

## 시스템 요구사항

- **macOS**: Monterey 이상 (Apple Silicon M3)
- **RAM**: 16GB (권장)
- **디스크**: 20GB 여유 공간
- **Python**: 3.10
- **Node.js**: 20.x

## 1. 사전 준비

### Homebrew 설치 (없는 경우)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Conda 설치 (없는 경우)

```bash
# Miniconda 다운로드 (Apple Silicon용)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh

# 설치 후 터미널 재시작
```

## 2. Ollama 설치 및 설정

### Ollama 설치

```bash
# Homebrew로 설치 (권장)
brew install ollama

# 또는 공식 사이트에서 다운로드
# https://ollama.com/download
```

### Ollama 서비스 시작

```bash
# 백그라운드 서비스로 시작
brew services start ollama

# 또는 직접 실행 (터미널에서)
ollama serve
```

### LLM 모델 다운로드

```bash
# Llama 3.1 8B 모델 다운로드 (약 4.9GB, 5-10분 소요)
ollama pull llama3.1:8b

# 모델 확인
ollama list

# 테스트
ollama run llama3.1:8b "안녕하세요"
```

**메모리 부족 시 경량 모델 사용:**
```bash
ollama pull llama3.2:3b  # 약 2GB
```

## 3. Python 환경 설정

### Conda 환경 생성

```bash
# 프로젝트 디렉토리로 이동
cd /Users/newkimjiwon/CODE/GDPP-AI-Docent-LLM-

# Conda 환경 생성
conda create -n gdpp python=3.10 -y

# 환경 활성화
conda activate gdpp
```

### Python 의존성 설치

```bash
# requirements.txt 설치
pip install -r requirements.txt

# 설치 확인
pip list | grep fastapi
```

### 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (선택사항)
nano .env
```

**`.env` 파일 내용 (기본값):**
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Vector DB
CHROMA_PERSIST_DIRECTORY=./data/vectordb
EMBEDDING_MODEL=jhgan/ko-sbert-nli

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# JWT Authentication
JWT_SECRET_KEY=your_super_secret_key_change_this
```

## 4. 벡터 데이터베이스 구축

```bash
# 프로젝트 루트에서 (최초 1회만 실행)
python src/rag/build_vectordb.py
```

**예상 출력:**
```
[INFO] 위키피디아 크롤링 시작 (12개 페이지)
[SUCCESS] 총 12개 페이지 크롤링 완료
[INFO] 64개 문서 임베딩 중...
[SUCCESS] 벡터 데이터베이스 구축 완료!
```

## 5. Node.js 환경 설정

### Node.js 설치

```bash
# Homebrew로 Node.js 20 설치
brew install node@20

# 또는 nvm 사용
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### React 프론트엔드 의존성 설치

```bash
cd /Users/newkimjiwon/CODE/GDPP-AI-Docent-LLM-/frontend

# 의존성 설치 (최초 1회만)
npm install
```

## 6. 서버 실행

### 터미널 1: 백엔드 서버

```bash
# Conda 환경 활성화
conda activate gdpp

# 프로젝트 루트로 이동
cd /Users/newkimjiwon/CODE/GDPP-AI-Docent-LLM-

# FastAPI 서버 시작
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**성공 시 출력:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 터미널 2: React 프론트엔드

```bash
# 프론트엔드 디렉토리로 이동
cd /Users/newkimjiwon/CODE/GDPP-AI-Docent-LLM-/frontend

# React 개발 서버 시작
npm run dev
```

**성공 시 출력:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 7. 접속 및 사용

### 웹 브라우저에서 접속

- **React 프론트엔드**: http://localhost:5173
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 사용 방법

1. **게스트 모드**: 로그인 없이 바로 채팅 시작
2. **질문 입력**: 하단 입력창에 질문 입력
3. **로그인**: 대화를 저장하려면 "로그인하여 저장" 클릭
4. **회원가입**: 새 계정 만들기
5. **대화 관리**: 왼쪽 사이드바에서 대화 목록 확인
6. **상품 저장**: 오른쪽 패널에서 관심 상품 URL 저장

### 예시 질문

**브랜드 정보:**
- "고양이 사료 추천해줘"
- "건강백서캣에 대해 알려줘"
- "F구역에 어떤 브랜드가 있어?"

**고양이 지식:**
- "고양이 품종은 어떤 것들이 있나요?"
- "페르시안 고양이에 대해 설명해줘"
- "고양이 건강 관리 방법은?"

## 문제 해결

### Ollama 연결 실패

```bash
# Ollama 상태 확인
brew services list | grep ollama

# Ollama 재시작
brew services restart ollama

# 또는 직접 실행
pkill ollama
ollama serve
```

### 백엔드 API 연결 실패

```bash
# 포트 8000 사용 중인지 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 프론트엔드 빌드 오류

```bash
# node_modules 삭제 후 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 메모리 부족

```bash
# 경량 모델로 변경
ollama pull llama3.2:3b

# .env 파일 수정
OLLAMA_MODEL=llama3.2:3b

# 백엔드 재시작
```

### ChromaDB 오류

```bash
# 벡터 DB 재구축
rm -rf data/vectordb
python src/rag/build_vectordb.py
```

## 성능 정보

### M3 칩 성능 (예상)

- **검색 속도**: ~100ms
- **LLM 응답 속도**: ~20-30 tokens/sec
- **메모리 사용량**: ~12-15GB (16GB RAM에서 안정적)
- **GPU 가속**: Metal 자동 사용

### 데이터 현황

- **Wikipedia 고양이 지식**: 12개 페이지
- **GDPP 브랜드**: 52개
- **총 청크**: 64개
- **임베딩 차원**: 768 (Ko-SBERT)

## 서버 종료

### 백엔드 종료

```bash
# Ctrl + C (터미널 1에서)
```

### 프론트엔드 종료

```bash
# Ctrl + C (터미널 2에서)
```

### Ollama 종료

```bash
# 백그라운드 서비스 중지
brew services stop ollama

# 또는 프로세스 종료
pkill ollama
```

## 유용한 명령어

### 시스템 모니터링

```bash
# 메모리 사용량 확인
top -l 1 | grep PhysMem

# CPU 사용량 확인
top -l 1 | grep "CPU usage"

# Ollama 프로세스 확인
ps aux | grep ollama
```

### 로그 확인

```bash
# Ollama 로그
brew services info ollama

# FastAPI 로그 (터미널 출력)
# 백엔드 실행 중인 터미널 확인
```

## 빠른 시작 스크립트

프로젝트 루트에 `start.sh` 생성:

```bash
#!/bin/bash

echo "GDPP AI Docent 시작..."

# Ollama 시작
echo "1. Ollama 시작..."
brew services start ollama
sleep 2

# 백엔드 시작 (백그라운드)
echo "2. 백엔드 시작..."
cd /Users/newkimjiwon/CODE/GDPP-AI-Docent-LLM-
conda activate gdpp
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &

# 프론트엔드 시작
echo "3. 프론트엔드 시작..."
cd frontend
npm run dev

echo "모든 서버가 시작되었습니다!"
echo "http://localhost:5173 에서 접속하세요"
```

**실행:**
```bash
chmod +x start.sh
./start.sh
```

## 참고 자료

- [Ollama 공식 문서](https://ollama.com/docs)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)
- [Apple Silicon 최적화 가이드](https://developer.apple.com/metal/)

**Made with Love for Cat Lovers on macOS**
