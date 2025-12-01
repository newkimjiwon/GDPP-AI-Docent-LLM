# Ollama 설치 가이드

## 현재 상황
- GPU: RTX 3090 24GB
- CUDA: 11.8
- 환경: WSL2

## 설치 방법

### 방법 1: 자동 설치 스크립트 (권장)
터미널에서 직접 실행:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

sudo 비밀번호 입력 필요

### 방법 2: 수동 다운로드
```bash
# Ollama 바이너리 다운로드
wget https://ollama.com/download/ollama-linux-amd64
sudo mv ollama-linux-amd64 /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama

# Ollama 서비스 시작
ollama serve
```

### 방법 3: Docker 사용
```bash
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## 설치 후 확인

```bash
# Ollama 버전 확인
ollama --version

# GPU 인식 확인
nvidia-smi

# 모델 다운로드 (한국어 모델)
ollama pull llama3.1:8b
```

## 다음 단계

설치 완료 후:
1. Ollama 서비스 시작
2. 모델 다운로드
3. API 테스트
4. FastAPI 백엔드 통합
