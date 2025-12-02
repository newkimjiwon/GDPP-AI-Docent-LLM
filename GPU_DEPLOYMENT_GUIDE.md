# GCP GPU 인스턴스 배포 가이드

이 가이드는 GCP에서 GPU 인스턴스를 생성하고, NVIDIA 드라이버를 설정한 후, GPU 가속을 지원하는 Docker 컨테이너를 배포하는 방법을 설명합니다.

## 1. GCP 인스턴스 생성 (GPU 포함)

GCP 콘솔에서 새 VM 인스턴스를 생성하거나 기존 인스턴스를 수정합니다.

### 권장 사양
- **머신 계열**: N1 또는 G2
- **머신 유형**: `n1-standard-4` (vCPU 4개, 15GB 메모리) 또는 `g2-standard-4`
- **GPU**: NVIDIA Tesla T4 x 1 (또는 L4)
- **부팅 디스크**: Ubuntu 22.04 LTS (x86/64), 크기 50GB 이상 (표준 영구 디스크 또는 SSD)
- **방화벽**: HTTP/HTTPS 트래픽 허용

> **참고**: 처음 GPU를 사용하는 경우 할당량(Quota) 증가 요청이 필요할 수 있습니다.

## 2. NVIDIA 드라이버 및 Docker 설정

인스턴스에 SSH로 접속한 후 다음 명령어를 순서대로 실행합니다.

### 2.1. NVIDIA Container Toolkit 설치

```bash
# 패키지 목록 업데이트 및 필수 도구 설치
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# NVIDIA Docker 저장소 키 추가
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# NVIDIA Container Toolkit 설치
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Docker 데몬 재시작
sudo systemctl restart docker
```

### 2.2. GPU 인식 확인

```bash
# NVIDIA 드라이버 상태 확인 (드라이버가 자동 설치된 경우)
nvidia-smi

# Docker에서 GPU 인식 확인
sudo docker run --rm --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
```

> `nvidia-smi` 명령어가 작동하지 않으면, GCP 인스턴스 생성 시 "NVIDIA GPU 드라이버 자동 설치" 옵션을 선택했는지 확인하거나 수동으로 드라이버를 설치해야 합니다.

## 3. 애플리케이션 배포

### 3.1. 코드 가져오기

```bash
cd ~/GDPP-AI-Docent-LLM
git pull origin main
```

### 3.2. GPU 모드로 실행

`docker-compose.gpu.yml` 파일을 사용하여 컨테이너를 실행합니다.

```bash
sudo docker-compose -f docker-compose.gpu.yml up -d --build
```

### 3.3. 로그 확인

```bash
sudo docker-compose -f docker-compose.gpu.yml logs -f ollama
```

로그에서 GPU 관련 메시지가 보이면 성공입니다.

## 4. 문제 해결

- **Error response from daemon: could not select device driver "" with capabilities: [[gpu]]**: NVIDIA Container Toolkit이 제대로 설치되지 않았거나 Docker가 재시작되지 않았습니다. 2.1단계를 다시 확인하세요.
- **Ollama가 느림**: GPU가 아닌 CPU로 실행 중일 수 있습니다. `nvidia-smi`로 GPU 사용량을 확인하세요.
