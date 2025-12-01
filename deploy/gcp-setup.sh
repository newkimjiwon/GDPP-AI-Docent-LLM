#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  GDPP AI Docent - GCP 배포 스크립트${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# GCP 프로젝트 설정
read -p "GCP 프로젝트 ID를 입력하세요: " PROJECT_ID
read -p "인스턴스 이름 (기본: gdpp-ai-docent): " INSTANCE_NAME
INSTANCE_NAME=${INSTANCE_NAME:-gdpp-ai-docent}
read -p "리전 (기본: asia-northeast3-a, 서울): " ZONE
ZONE=${ZONE:-asia-northeast3-a}

echo ""
echo -e "${YELLOW}설정 확인:${NC}"
echo "  프로젝트 ID: $PROJECT_ID"
echo "  인스턴스 이름: $INSTANCE_NAME"
echo "  리전: $ZONE"
echo ""
read -p "계속하시겠습니까? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "취소되었습니다."
    exit 1
fi

echo ""
echo -e "${GREEN}[1/5] GCE 인스턴스 생성 중...${NC}"

gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --maintenance-policy=TERMINATE \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-ssd \
    --metadata=install-nvidia-driver=True \
    --tags=http-server,https-server \
    --scopes=https://www.googleapis.com/auth/cloud-platform

if [ $? -ne 0 ]; then
    echo -e "${RED}인스턴스 생성 실패!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[2/5] 방화벽 규칙 생성 중...${NC}"

# HTTP 허용
gcloud compute firewall-rules create allow-http-$INSTANCE_NAME \
    --project=$PROJECT_ID \
    --allow=tcp:80 \
    --target-tags=http-server \
    --description="Allow HTTP traffic for GDPP AI Docent" \
    2>/dev/null || echo "방화벽 규칙이 이미 존재합니다."

echo ""
echo -e "${GREEN}[3/5] 외부 IP 확인 중...${NC}"

EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo -e "${GREEN}외부 IP: $EXTERNAL_IP${NC}"

echo ""
echo -e "${GREEN}[4/5] 인스턴스 준비 대기 중 (60초)...${NC}"
sleep 60

echo ""
echo -e "${GREEN}[5/5] 배포 완료!${NC}"
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  다음 단계:${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "1. SSH 접속:"
echo -e "   ${GREEN}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
echo "2. 서버에서 실행:"
echo -e "   ${GREEN}curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/install-docker.sh | bash${NC}"
echo "   또는 수동으로:"
echo -e "   ${GREEN}git clone YOUR_REPO${NC}"
echo -e "   ${GREEN}cd GDDPAIDocent${NC}"
echo -e "   ${GREEN}./deploy/install-docker.sh${NC}"
echo -e "   ${GREEN}./deploy/deploy-app.sh${NC}"
echo ""
echo "3. 접속:"
echo -e "   ${GREEN}http://$EXTERNAL_IP${NC}"
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  비용 절약 팁:${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "인스턴스 중지 (과금 중지):"
echo -e "  ${GREEN}gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
echo "인스턴스 시작:"
echo -e "  ${GREEN}gcloud compute instances start $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
echo "인스턴스 삭제 (완전 제거):"
echo -e "  ${GREEN}gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
