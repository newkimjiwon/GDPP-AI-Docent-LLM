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

```bash
# 최신 코드 가져오기
git pull origin test-gcp  # 또는 main

# Docker 컨테이너 빌드 및 실행
sudo docker compose up -d --build
```

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

## 5. 주요 명령어

```bash
# 로그 확인 (실시간)
sudo docker compose logs -f

# 백엔드 로그만 확인
sudo docker compose logs -f backend

# 컨테이너 상태 확인
sudo docker compose ps

# 서비스 중지
sudo docker compose down
```
