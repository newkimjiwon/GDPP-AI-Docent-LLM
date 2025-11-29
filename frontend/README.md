# Frontend 디렉토리

## 개요

React + Vite + Tailwind CSS 기반의 ChatGPT 스타일 프론트엔드입니다.

## 디렉토리 구조

```
frontend/
├── src/
│   ├── components/      # React 컴포넌트
│   ├── pages/          # 페이지 컴포넌트
│   ├── services/       # API 서비스
│   ├── store/          # Zustand 상태 관리
│   ├── App.jsx         # 메인 앱
│   ├── main.jsx        # 엔트리 포인트
│   └── index.css       # 전역 스타일
├── public/             # 정적 파일
├── node_modules/       # 의존성
├── package.json        # 패키지 설정
├── vite.config.js      # Vite 설정
├── tailwind.config.js  # Tailwind 설정
└── postcss.config.js   # PostCSS 설정
```

## 주요 컴포넌트

### ChatArea.jsx
채팅 메시지를 표시하고 입력을 받는 메인 영역입니다.

**기능**
- 메시지 목록 표시
- 사용자/AI 메시지 구분
- 참고 자료 표시
- 로딩 애니메이션
- 자동 스크롤

### Sidebar.jsx
대화 목록을 표시하는 왼쪽 사이드바입니다.

**기능**
- 대화 목록 표시
- 새 대화 생성
- 대화 선택
- 대화 삭제
- 게스트 모드 안내
- 로그인/로그아웃 버튼

### ProductPanel.jsx
상품 URL을 저장하고 관리하는 오른쪽 패널입니다.

**기능**
- URL 입력 및 추가
- URL 목록 표시
- URL 클릭 시 새 탭 열기
- URL 삭제
- 총 상품 개수 표시

## 상태 관리

### authStore.js
사용자 인증 상태를 관리합니다.

**상태**
- `user`: 현재 사용자 정보
- `token`: JWT 토큰
- `isAuthenticated`: 로그인 여부
- `isLoading`: 로딩 상태
- `error`: 에러 메시지

**액션**
- `login()`: 로그인
- `register()`: 회원가입
- `logout()`: 로그아웃
- `clearError()`: 에러 초기화

### chatStore.js
채팅 및 대화 상태를 관리합니다.

**상태**
- `conversations`: 대화 목록
- `currentConversation`: 현재 대화
- `messages`: 메시지 목록
- `isLoading`: 로딩 상태
- `error`: 에러 메시지

**액션**
- `fetchConversations()`: 대화 목록 조회
- `createConversation()`: 대화 생성
- `selectConversation()`: 대화 선택
- `sendMessage()`: 메시지 전송
- `deleteConversation()`: 대화 삭제

## 실행 방법

### 개발 서버
```bash
npm run dev
```

### 빌드
```bash
npm run build
```

### 프리뷰
```bash
npm run preview
```

## 환경 설정

### Node.js 버전
Node.js 20 LTS 이상 필요합니다.

```bash
# nvm 사용
nvm install 20
nvm use 20
```

### 의존성 설치
```bash
npm install
```

## 주요 의존성

- `react`: ^18.3.1
- `react-dom`: ^18.3.1
- `react-router-dom`: ^7.1.1
- `zustand`: ^5.0.2
- `axios`: ^1.7.9
- `tailwindcss`: ^3.4.0
