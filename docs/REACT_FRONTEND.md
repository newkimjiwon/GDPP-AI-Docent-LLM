# React 프론트엔드 구현 (2025-11-30)

## 개요

기존 Streamlit 프론트엔드를 React 기반으로 전환하여 ChatGPT 스타일의 현대적인 UI를 구현했습니다.

## 주요 변경 사항

### 1. 백엔드 인증 시스템 구축

**데이터베이스 설정**
- SQLAlchemy + SQLite 사용
- 데이터베이스 파일: `./data/gdpp.db`
- 자동 테이블 생성 (`init_db()`)

**데이터 모델**
- `User`: 사용자 정보 (id, email, password_hash, created_at)
- `Folder`: 대화 폴더 (id, user_id, name, created_at)
- `Conversation`: 대화 세션 (id, user_id, folder_id, title, created_at, updated_at)
- `Message`: 개별 메시지 (id, conversation_id, role, content, sources, created_at)

**인증 시스템**
- JWT 토큰 기반 인증
- bcrypt를 사용한 비밀번호 해싱
- 이메일/비밀번호 로그인

**API 엔드포인트**
- `POST /api/auth/register`: 회원가입
- `POST /api/auth/login`: 로그인
- `GET /api/auth/me`: 현재 사용자 정보

### 2. 대화 관리 API

**폴더 관리**
- `GET /api/folders/`: 폴더 목록 조회
- `POST /api/folders/`: 폴더 생성
- `PUT /api/folders/{folder_id}`: 폴더 수정
- `DELETE /api/folders/{folder_id}`: 폴더 삭제

**대화 관리**
- `GET /api/conversations/`: 대화 목록 조회
- `POST /api/conversations/`: 대화 생성
- `GET /api/conversations/{conversation_id}`: 대화 상세 조회
- `PUT /api/conversations/{conversation_id}`: 대화 수정
- `DELETE /api/conversations/{conversation_id}`: 대화 삭제
- `POST /api/conversations/{conversation_id}/messages`: 메시지 추가

### 3. React 프론트엔드

**기술 스택**
- Vite: 빌드 도구
- React 18: UI 라이브러리
- Tailwind CSS 3: 스타일링
- Zustand: 상태 관리
- Axios: HTTP 클라이언트
- React Router: 라우팅

**프로젝트 구조**
```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatArea.jsx       # 채팅 영역
│   │   ├── Sidebar.jsx         # 대화 목록 사이드바
│   │   └── ProductPanel.jsx    # 상품 URL 패널
│   ├── pages/
│   │   ├── Login.jsx           # 로그인 페이지
│   │   ├── Register.jsx        # 회원가입 페이지
│   │   └── Chat.jsx            # 메인 채팅 페이지
│   ├── services/
│   │   ├── api.js              # Axios 클라이언트
│   │   └── auth.js             # 인증 서비스
│   ├── store/
│   │   ├── authStore.js        # 인증 상태 관리
│   │   └── chatStore.js        # 채팅 상태 관리
│   ├── App.jsx                 # 메인 앱 컴포넌트
│   ├── main.jsx                # 엔트리 포인트
│   └── index.css               # Tailwind CSS
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

**주요 기능**

**게스트 모드**
- 로그인 없이 바로 채팅 가능
- 대화 내용은 임시로만 저장 (새로고침 시 사라짐)
- 사이드바에 "게스트 모드" 안내 표시
- "로그인하여 저장" 버튼 제공

**로그인 사용자**
- 대화 히스토리 저장 및 불러오기
- 폴더로 대화 정리
- 대화 제목 수정
- 대화 삭제

**UI 구성**
- 왼쪽: 대화 목록 사이드바
- 중앙: 채팅 영역
- 오른쪽: 상품 URL 보관 패널

**상품 URL 패널**
- URL 입력 및 추가
- 저장된 URL 목록 표시
- URL 클릭 시 새 탭에서 열기
- 개별 URL 삭제

### 4. LLM 응답 길이 개선

**문제**
- `max_tokens`가 512로 설정되어 응답이 중간에 잘림

**해결**
- `max_tokens`를 512 → 2048로 증가
- 약 1500-2000 단어까지 응답 가능

**수정 파일**
- `src/api/routes/chat.py`
- `src/model/ollama_client.py`

## 실행 방법

### 백엔드 실행
```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### React 프론트엔드 실행
```bash
# nvm 환경 로드
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# 프론트엔드 실행
cd frontend
npm run dev
```

브라우저에서 http://localhost:5173 접속

## 주요 이슈 및 해결

### 1. bcrypt 호환성 문제
**문제**: `passlib`와 `bcrypt` 라이브러리 버전 호환성 문제
**해결**: `passlib` 제거하고 `bcrypt`를 직접 사용

### 2. Node.js 버전 문제
**문제**: Ubuntu 기본 Node.js 버전이 너무 낮음 (v12)
**해결**: nvm을 사용하여 Node.js 20 LTS 설치

### 3. Tailwind CSS 버전 문제
**문제**: Tailwind CSS v4의 PostCSS 플러그인 분리
**해결**: Tailwind CSS v3.4.0으로 다운그레이드

### 4. 스크롤 문제
**문제**: 메시지가 많아지면 화면이 넘어감
**해결**: 
- Chat 페이지에 `overflow-hidden` 추가
- ChatArea와 ProductPanel에 `h-full` 추가
- 메시지 영역에 `min-h-0` 추가

## 다음 단계

1. 대화 히스토리 저장 기능 완성
2. 폴더 관리 UI 구현
3. 스트리밍 응답 지원
4. 반응형 디자인 개선
5. 에러 처리 강화
