# GDPP AI Docent - 프로젝트 진행 상황

## 완료된 작업

### Phase 1: 환경 설정 및 프로젝트 구조 [완료]
- Python 3.10 가상환경 설정 (gdpp)
- 프로젝트 디렉토리 구조 생성
- requirements.txt 작성
- 환경 변수 템플릿 (.env.example) 생성

### Phase 2: 데이터 엔지니어링 [완료]
- **Wikipedia 크롤러**: 고양이 관련 지식 12개 페이지 수집 (27,081자)
- **GDPP 브랜드 데이터**: 52개 브랜드 정보 구조화
- **Semantic Chunking**: 64개 청크 생성 (평균 487자)
- **Metadata Extraction**: 소스, 카테고리, URL 등 메타데이터 추출

### Phase 3: RAG 시스템 구축 [완료]
- **Ko-SBERT 임베딩**: jhgan/ko-sbert-nli 모델 (768차원)
- **ChromaDB 벡터 DB**: 64개 청크 임베딩 및 저장
- **Hybrid Search**: Dense Vector Search + Sparse BM25 Search
- **검색 성능**: 브랜드 및 Wikipedia 쿼리 정확도 검증 완료

## 데이터 현황

### 수집된 데이터
- **Wikipedia 지식**: 12개 페이지
  - 고양이, 고양이 품종, 페르시안, 샴, 러시안 블루, 메인쿤 등
  - 총 27,081자
  
- **GDPP 브랜드**: 52개 브랜드
  - 사료/간식: 15개
  - 용품: 18개
  - 헬스케어: 6개
  - 아트: 13개

### RAG 시스템 현황
- **임베딩 모델**: Ko-SBERT (768차원)
- **벡터 DB**: ChromaDB (64개 문서)
- **검색 방식**: Hybrid Search (Vector 70% + BM25 30%)

## 다음 단계

### Phase 4: LLM 서빙 [다음 작업]
로컬 LLM 구축은 시간과 리소스가 많이 소요되므로, 빠른 프로토타이핑을 위해 다음 옵션 중 선택 필요:

**옵션 A: 간단한 프로토타입 (권장)**
- Streamlit + OpenAI API (또는 Google Gemini API)
- RAG 시스템만 로컬에서 구동
- 빠른 개발 및 데모 가능

**옵션 B: 완전한 로컬 시스템**
- LG EXAONE 3.0 모델 다운로드 및 설정
- vLLM 서빙 엔진 구성
- GPU 필요 (최소 8GB VRAM)
- 개발 시간: 2-3일 추가

### Phase 5: 백엔드 API (옵션 A 선택 시)
- FastAPI 프로젝트 초기화
- /chat 엔드포인트 구현
- RAG 시스템 통합

### Phase 6: 프론트엔드 (옵션 A 선택 시)
- Streamlit 챗봇 UI 구현
- 빠른 프로토타이핑

## 참고사항

- 현재까지 외부 API 없이 로컬 데이터로 RAG 시스템 구축 완료
- 검색 기능은 정상 작동 확인
- LLM 선택에 따라 개발 일정 및 난이도 변경
- 제출 기한: 2025년 12월 5일 (약 7일 남음)
