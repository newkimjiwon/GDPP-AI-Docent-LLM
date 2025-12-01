# GCP 배포 가이드

## 목차
1. [사전 준비](#사전-준비)
2. [로컬 테스트](#로컬-테스트)
3. [GCP 배포](#gcp-배포)
4. [비용 관리](#비용-관리)
5. [문제 해결](#문제-해결)

---

## 사전 준비

### 1. GCP 계정 설정

**신규 계정 (추천)**:
- GCP 신규 가입 시 $300 크레딧 제공 (90일간)
- 크레딧으로 GPU 인스턴스 무료 사용 가능
- 가입: https://cloud.google.com/free

**기존 계정**:
- 결제 계정 활성화 필요
- 예상 비용: 3일 배포 시 약 $42 (₩55,000)

### 2. gcloud CLI 설치

```bash
# Linux/WSL
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# macOS
brew install --cask google-cloud-sdk

# 로그인
gcloud init
gcloud auth login
```

### 3. 프로젝트 생성

```bash
# GCP 콘솔에서 프로젝트 생성
# 또는 CLI로:
gcloud projects create gdpp-ai-docent-demo --name="GDPP AI Docent"
gcloud config set project gdpp-ai-docent-demo
```

---

## 로컬 테스트

배포 전에 로컬에서 Docker로 테스트하세요.

### 1. 벡터 DB 구축

```bash
cd /mnt/d/Project/GDDPAIDocent
conda activate gdpp
python src/rag/build_vectordb.py
```

### 2. Docker Compose 실행

```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 테스트

```bash
# 프론트엔드
curl http://localhost

# 백엔드 API
curl http://localhost:8000/api/status

# Ollama
curl http://localhost:11434/
```

### 4. 중지

```bash
docker-compose down
```

---

## GCP 배포

### 단계 1: GCE 인스턴스 생성

```bash
cd /mnt/d/Project/GDDPAIDocent
./deploy/gcp-setup.sh
```

**입력 정보**:
- GCP 프로젝트 ID: `gdpp-ai-docent-demo`
- 인스턴스 이름: `gdpp-ai-docent` (기본값)
- 리전: `asia-northeast3-a` (서울, 기본값)

**생성되는 리소스**:
- GCE 인스턴스: n1-standard-4 (4 vCPU, 15GB RAM)
- GPU: NVIDIA T4 (16GB)
- 디스크: 100GB SSD
- 방화벽: HTTP (포트 80) 허용

**예상 시간**: 약 2-3분

### 단계 2: SSH 접속

```bash
gcloud compute ssh gdpp-ai-docent --zone=asia-northeast3-a
```

### 단계 3: 코드 업로드

**방법 1: Git Clone (추천)**
```bash
# 서버에서 실행
git clone https://github.com/YOUR_USERNAME/GDDPAIDocent.git
cd GDDPAIDocent
```

**방법 2: SCP로 파일 전송**
```bash
# 로컬에서 실행
gcloud compute scp --recurse /mnt/d/Project/GDDPAIDocent \
    gdpp-ai-docent:~/ --zone=asia-northeast3-a
```

### 단계 4: Docker 설치

```bash
# 서버에서 실행
cd GDDPAIDocent
./deploy/install-docker.sh

# 로그아웃 후 재접속 (Docker 그룹 권한 적용)
exit
gcloud compute ssh gdpp-ai-docent --zone=asia-northeast3-a
```

### 단계 5: 애플리케이션 배포

```bash
cd GDDPAIDocent
./deploy/deploy-app.sh
```

**배포 과정**:
1. 환경 변수 설정
2. 벡터 DB 구축 (최초 1회)
3. Docker 이미지 빌드 (5-10분)
4. 컨테이너 시작
5. Ollama 모델 다운로드 (5분)

**예상 시간**: 약 15-20분

### 단계 6: 접속 확인

```bash
# 외부 IP 확인
gcloud compute instances describe gdpp-ai-docent \
    --zone=asia-northeast3-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# 예시: 34.64.123.45
```

**브라우저에서 접속**:
- 프론트엔드: `http://34.64.123.45`
- 백엔드 API: `http://34.64.123.45:8000`
- API 문서: `http://34.64.123.45:8000/docs`

---

## 비용 관리

### 비용 모니터링

**GCP 콘솔에서 확인**:
1. https://console.cloud.google.com/billing
2. "예산 및 알림" 설정
3. 알림 임계값: $50, $100

**CLI로 확인**:
```bash
gcloud billing accounts list
gcloud billing projects describe gdpp-ai-docent-demo
```

### 예상 비용 (서울 리전)

| 항목 | 시간당 | 일일 | 3일 |
|------|--------|------|-----|
| n1-standard-4 | $0.19 | $4.56 | $13.68 |
| NVIDIA T4 GPU | $0.35 | $8.40 | $25.20 |
| 100GB SSD | - | $0.57 | $1.70 |
| 네트워크 (10GB) | - | - | $1.20 |
| **총 비용** | **$0.54** | **$12.96** | **$41.78** |

**신규 계정**: $300 크레딧으로 완전 무료! ✅

### 비용 절감 팁

**1. 사용하지 않을 때 중지**
```bash
# 인스턴스 중지 (과금 중지, 디스크 비용만 발생)
gcloud compute instances stop gdpp-ai-docent --zone=asia-northeast3-a

# 인스턴스 시작
gcloud compute instances start gdpp-ai-docent --zone=asia-northeast3-a
```

**중지 시 비용**: 디스크만 과금 (~$0.57/일)

**2. 완전 삭제**
```bash
# 인스턴스 삭제 (모든 과금 중지)
gcloud compute instances delete gdpp-ai-docent --zone=asia-northeast3-a

# 방화벽 규칙 삭제
gcloud compute firewall-rules delete allow-http-gdpp-ai-docent
```

**3. 스케줄링 (선택사항)**
```bash
# 매일 밤 12시에 자동 중지
gcloud compute resource-policies create instance-schedule stop-at-midnight \
    --region=asia-northeast3 \
    --vm-start-schedule='0 9 * * *' \
    --vm-stop-schedule='0 0 * * *' \
    --timezone='Asia/Seoul'
```

---

## 문제 해결

### 1. Docker 빌드 실패

**증상**: `docker-compose build` 실패

**해결**:
```bash
# Docker 재시작
sudo systemctl restart docker

# 캐시 없이 재빌드
docker-compose build --no-cache
```

### 2. Ollama 모델 다운로드 실패

**증상**: `ollama pull` 실패

**해결**:
```bash
# Ollama 컨테이너 재시작
docker-compose restart ollama

# 수동으로 모델 다운로드
docker exec -it gdpp-ollama ollama pull llama3.1:8b
```

### 3. GPU 인식 안 됨

**증상**: `nvidia-smi` 명령 실패

**해결**:
```bash
# NVIDIA 드라이버 확인
nvidia-smi

# 드라이버 재설치
sudo apt-get install -y nvidia-driver-535
sudo reboot
```

### 4. 포트 80 접속 안 됨

**증상**: 브라우저에서 접속 불가

**해결**:
```bash
# 방화벽 규칙 확인
gcloud compute firewall-rules list

# 방화벽 규칙 재생성
gcloud compute firewall-rules create allow-http-gdpp-ai-docent \
    --allow=tcp:80 \
    --target-tags=http-server
```

### 5. 메모리 부족

**증상**: 컨테이너가 자주 재시작됨

**해결**:
```bash
# 메모리 사용량 확인
docker stats

# 불필요한 컨테이너 제거
docker system prune -a
```

### 6. 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama

# 최근 100줄만
docker-compose logs --tail=100
```

---

## 유용한 명령어

### Docker 관리

```bash
# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart

# 컨테이너 중지
docker-compose stop

# 컨테이너 시작
docker-compose start

# 컨테이너 삭제 (데이터 유지)
docker-compose down

# 컨테이너 및 볼륨 삭제 (데이터 삭제)
docker-compose down -v
```

### GCP 관리

```bash
# 인스턴스 목록
gcloud compute instances list

# 인스턴스 상세 정보
gcloud compute instances describe gdpp-ai-docent --zone=asia-northeast3-a

# SSH 접속
gcloud compute ssh gdpp-ai-docent --zone=asia-northeast3-a

# 파일 전송 (로컬 → 서버)
gcloud compute scp local-file.txt gdpp-ai-docent:~/ --zone=asia-northeast3-a

# 파일 전송 (서버 → 로컬)
gcloud compute scp gdpp-ai-docent:~/remote-file.txt ./ --zone=asia-northeast3-a
```

---

## 다음 단계

### 도메인 연결 (선택사항)

1. **도메인 구매**: Namecheap, GoDaddy 등
2. **DNS 설정**: A 레코드를 GCE 외부 IP로 설정
3. **HTTPS 설정**: Let's Encrypt + Nginx

### 데이터베이스 업그레이드 (선택사항)

SQLite → Cloud SQL (PostgreSQL)로 마이그레이션

### 모니터링 (선택사항)

- Google Cloud Monitoring
- Prometheus + Grafana
- Sentry (에러 추적)

---

## 참고 자료

- [GCP 공식 문서](https://cloud.google.com/docs)
- [Docker 공식 문서](https://docs.docker.com/)
- [Ollama 공식 문서](https://ollama.com/docs)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

---

**Made with ❤️ for Cat Lovers**
