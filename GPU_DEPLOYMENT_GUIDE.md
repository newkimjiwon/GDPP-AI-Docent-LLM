# GPU 배포 가이드

GCP에서 NVIDIA GPU를 사용하여 Ollama를 실행하는 방법입니다.

## 📋 사전 요구사항

- GCP 계정
- NVIDIA GPU가 포함된 인스턴스 (T4, L4, A100 등)
- Docker 및 Docker Compose 설치

## 🚀 GPU 인스턴스 생성

### 1. GCP 콘솔에서 인스턴스 생성

```bash
# 머신 타입: n1-standard-4 (또는 더 큰 타입)
# GPU: NVIDIA Tesla T4 (1개)
# 부팅 디스크: Ubuntu 22.04 LTS
# 방화벽: HTTP, HTTPS 트래픽 허용
```

### 2. GPU 드라이버 설치 (자동)

인스턴스 생성 시 "GPU 드라이버 자동 설치" 옵션 선택

또는 수동 설치:
```bash
# NVIDIA 드라이버 설치
sudo apt-get update
sudo apt-get install -y nvidia-driver-535

# 재부팅
sudo reboot

# 확인
nvidia-smi
```

## 🐳 NVIDIA Docker 설치

```bash
# NVIDIA Container Toolkit 설치
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Docker 재시작
sudo systemctl restart docker

# 테스트
sudo docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## 📦 프로젝트 배포

### 1. 코드 가져오기

```bash
git clone https://github.com/newkimjiwon/GDPP-AI-Docent-LLM.git
cd GDPP-AI-Docent-LLM
```

### 2. 환경변수 설정

```bash
# 프론트엔드 환경변수
cd frontend
cp .env.production .env.local
# .env.local 파일에서 IP 주소 확인/수정
cd ..
```

### 3. GPU 버전으로 실행

```bash
# GPU 지원 Docker Compose 사용
sudo docker-compose -f docker-compose.gpu.yml up -d

# 로그 확인
sudo docker-compose -f docker-compose.gpu.yml logs -f
```

### 4. GPU 인식 확인

```bash
# Ollama 컨테이너에서 GPU 확인
sudo docker exec -it gdpp-ollama nvidia-smi

# 예상 출력:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx    CUDA Version: 12.2     |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
# | N/A   xx°C    P0    xxW / 70W |      0MiB / 15360MiB |      0%      Default |
# +-------------------------------+----------------------+----------------------+
```

### 5. 모델 다운로드

```bash
# Ollama 컨테이너에서 모델 다운로드
sudo docker exec -it gdpp-ollama ollama pull llama3.1:8b

# 모델 확인
sudo docker exec -it gdpp-ollama ollama list
```

## 🧪 성능 테스트

브라우저에서 `http://[GCP-IP]:8000` 접속 후 채팅 테스트:

**CPU vs GPU 성능 비교**:
- CPU (4코어): 응답 시간 30-60초
- GPU (T4): 응답 시간 3-5초 ⚡ (약 10배 빠름)

## 🔧 문제 해결

### GPU가 인식되지 않는 경우

```bash
# NVIDIA 드라이버 확인
nvidia-smi

# Docker에서 GPU 접근 확인
sudo docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# NVIDIA Container Toolkit 재설치
sudo apt-get install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

### 컨테이너 재시작

```bash
# 전체 재시작
sudo docker-compose -f docker-compose.gpu.yml down
sudo docker-compose -f docker-compose.gpu.yml up -d

# Ollama만 재시작
sudo docker-compose -f docker-compose.gpu.yml restart ollama
```

## 💰 비용 최적화

### 인스턴스 중지/시작

사용하지 않을 때는 인스턴스를 중지하여 비용 절감:

```bash
# GCP 콘솔에서 인스턴스 중지
# 또는 gcloud 명령어 사용
gcloud compute instances stop [INSTANCE_NAME]

# 재시작
gcloud compute instances start [INSTANCE_NAME]
```

### 비용 예상 (서울 리전 기준)

| GPU 타입 | 시간당 비용 | 월 비용 (24시간) | 성능 |
|---------|-----------|----------------|------|
| T4 | ~₩450 | ~₩324,000 | CPU 대비 10배 |
| L4 | ~₩900 | ~₩648,000 | T4 대비 2배 |
| A100 | ~₩4,700 | ~₩3,384,000 | 최고 성능 |

## 📝 참고사항

- GPU 사용 시 전력 소비가 증가하므로 비용이 상승합니다
- T4 GPU는 가성비가 좋아 10명 정도의 사용자에게 적합합니다
- 더 많은 사용자를 지원하려면 L4 또는 A100을 고려하세요
- CPU 버전(`docker-compose.yml`)도 계속 사용 가능합니다
