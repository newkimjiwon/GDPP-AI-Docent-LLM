#!/bin/bash

# NVIDIA Container Toolkit 설치 스크립트 (WSL2용)

echo "=========================================="
echo "  NVIDIA Container Toolkit 설치 (WSL2)"
echo "=========================================="
echo ""

# 1. 저장소 추가
echo "[1/4] NVIDIA Container Toolkit 저장소 추가..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. 패키지 업데이트
echo ""
echo "[2/4] 패키지 목록 업데이트..."
sudo apt-get update

# 3. NVIDIA Container Toolkit 설치
echo ""
echo "[3/4] NVIDIA Container Toolkit 설치..."
sudo apt-get install -y nvidia-container-toolkit

# 4. Docker 설정
echo ""
echo "[4/4] Docker 설정..."
sudo nvidia-ctk runtime configure --runtime=docker
sudo service docker restart

echo ""
echo "=========================================="
echo "  설치 완료!"
echo "=========================================="
echo ""
echo "GPU 테스트:"
echo "  docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu20.04 nvidia-smi"
echo ""
