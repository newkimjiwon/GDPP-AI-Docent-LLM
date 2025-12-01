#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Docker 및 NVIDIA 드라이버 설치${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}[1/5] 시스템 업데이트...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${YELLOW}[2/5] Docker 설치...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

echo ""
echo -e "${YELLOW}[3/5] Docker Compose 설치...${NC}"
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo ""
echo -e "${YELLOW}[4/5] NVIDIA Container Toolkit 설치...${NC}"
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

echo ""
echo -e "${YELLOW}[5/5] 설치 확인...${NC}"
docker --version
docker-compose --version
nvidia-smi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  설치 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}주의: 새 그룹 권한을 적용하려면 로그아웃 후 다시 로그인하세요.${NC}"
echo ""
