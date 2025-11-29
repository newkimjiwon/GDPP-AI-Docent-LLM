# 백엔드 인증 시스템

## 개요

JWT 토큰 기반의 사용자 인증 시스템입니다.

## 데이터베이스

**엔진**: SQLite
**파일 위치**: `./data/gdpp.db`
**ORM**: SQLAlchemy

## 모델

### User
사용자 계정 정보를 저장합니다.

**필드**
- `id`: Integer (Primary Key)
- `email`: String (Unique, 이메일 주소)
- `password_hash`: String (bcrypt 해시)
- `created_at`: DateTime (생성 시각)

**관계**
- `folders`: Folder 목록
- `conversations`: Conversation 목록

### Folder
대화를 그룹화하는 폴더입니다.

**필드**
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key → User)
- `name`: String (폴더 이름)
- `created_at`: DateTime (생성 시각)

**관계**
- `user`: User
- `conversations`: Conversation 목록

### Conversation
사용자와 AI 간의 대화 세션입니다.

**필드**
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key → User)
- `folder_id`: Integer (Foreign Key → Folder, Nullable)
- `title`: String (대화 제목)
- `created_at`: DateTime (생성 시각)
- `updated_at`: DateTime (수정 시각)

**관계**
- `user`: User
- `folder`: Folder
- `messages`: Message 목록

### Message
대화 내의 개별 메시지입니다.

**필드**
- `id`: Integer (Primary Key)
- `conversation_id`: Integer (Foreign Key → Conversation)
- `role`: String (user/assistant)
- `content`: Text (메시지 내용)
- `sources`: JSON (참고 자료, Nullable)
- `created_at`: DateTime (생성 시각)

**관계**
- `conversation`: Conversation

## 인증 흐름

### 회원가입
1. 사용자가 이메일/비밀번호 입력
2. 이메일 중복 확인
3. 비밀번호를 bcrypt로 해싱
4. 사용자 정보 DB 저장
5. JWT 토큰 발급 및 반환

### 로그인
1. 사용자가 이메일/비밀번호 입력
2. 이메일로 사용자 조회
3. 비밀번호 검증 (bcrypt.checkpw)
4. JWT 토큰 발급 및 반환

### 인증 확인
1. 클라이언트가 Authorization 헤더에 토큰 포함
2. 서버가 토큰 검증
3. 토큰에서 user_id 추출
4. DB에서 사용자 정보 조회
5. 사용자 객체 반환

## 보안

### 비밀번호 해싱
- **알고리즘**: bcrypt
- **라이브러리**: `bcrypt` (직접 사용)
- **솔트**: 자동 생성 (bcrypt.gensalt())

### JWT 토큰
- **알고리즘**: HS256
- **만료 시간**: 30일
- **SECRET_KEY**: 환경 변수로 관리 필요 (현재 하드코딩)

## API 엔드포인트

### POST /api/auth/register
회원가입

**요청**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### POST /api/auth/login
로그인

**요청**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### GET /api/auth/me
현재 사용자 정보 조회

**헤더**
```
Authorization: Bearer {token}
```

**응답**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-11-30T00:00:00"
}
```

## 향후 개선 사항

1. SECRET_KEY를 `.env` 파일로 이동
2. 토큰 갱신 (Refresh Token) 구현
3. 이메일 인증 추가
4. 비밀번호 재설정 기능
5. 계정 삭제 기능
6. 로그인 시도 제한 (Rate Limiting)
