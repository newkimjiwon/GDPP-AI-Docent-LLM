#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  GDPP AI Docent 애플리케이션 배포${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 프로젝트 디렉토리로 이동
cd "$(dirname "$0")/.." || exit 1

echo -e "${YELLOW}[1/6] 환경 변수 설정...${NC}"
if [ ! -f .env.production ]; then
    echo -e "${RED}.env.production 파일이 없습니다!${NC}"
    exit 1
fi

# JWT Secret 생성
JWT_SECRET=$(openssl rand -hex 32)
sed -i "s/your-super-secret-key-change-this-in-production-\$(openssl rand -hex 32)/$JWT_SECRET/" .env.production

echo ""
echo -e "${YELLOW}[2/6] 벡터 데이터베이스 구축...${NC}"
if [ ! -d "data/vectordb" ]; then
    echo "벡터 DB를 구축합니다 (최초 1회, 약 1분 소요)..."
    python3 src/rag/build_vectordb.py || {
        echo -e "${RED}벡터 DB 구축 실패! Docker 컨테이너에서 구축합니다.${NC}"
    }
fi

echo ""
echo -e "${YELLOW}[3/6] Docker 이미지 빌드...${NC}"
docker-compose build

echo ""
echo -e "${YELLOW}[4/6] Docker 컨테이너 시작...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}[5/6] Ollama 모델 다운로드 (약 5분 소요)...${NC}"
echo "모델 다운로드 중... 잠시만 기다려주세요."
docker exec gdpp-ollama ollama pull llama3.1:8b

echo ""
echo -e "${YELLOW}[6/6] 서비스 상태 확인...${NC}"
sleep 5
docker-compose ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 외부 IP 확인
EXTERNAL_IP=$(curl -s ifconfig.me)
echo -e "${GREEN}프론트엔드: http://$EXTERNAL_IP${NC}"
echo -e "${GREEN}백엔드 API: http://$EXTERNAL_IP:8000${NC}"
echo -e "${GREEN}API 문서: http://$EXTERNAL_IP:8000/docs${NC}"
echo ""
echo -e "${YELLOW}로그 확인:${NC}"
echo -e "  전체: ${GREEN}docker-compose logs -f${NC}"
echo -e "  백엔드: ${GREEN}docker-compose logs -f backend${NC}"
echo -e "  프론트엔드: ${GREEN}docker-compose logs -f frontend${NC}"
echo -e "  Ollama: ${GREEN}docker-compose logs -f ollama${NC}"
echo ""
echo -e "${YELLOW}서비스 중지:${NC}"
echo -e "  ${GREEN}docker-compose down${NC}"
echo ""
echo -e "${YELLOW}서비스 재시작:${NC}"
echo -e "  ${GREEN}docker-compose restart${NC}"
echo ""
