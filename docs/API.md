# 백엔드 API 문서

## 인증 API

### 회원가입
```http
POST /api/auth/register
Content-Type: application/json

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

### 로그인
```http
POST /api/auth/login
Content-Type: application/json

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

### 현재 사용자 정보
```http
GET /api/auth/me
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

## 폴더 API

### 폴더 목록 조회
```http
GET /api/folders/
Authorization: Bearer {token}
```

### 폴더 생성
```http
POST /api/folders/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Work Projects"
}
```

### 폴더 수정
```http
PUT /api/folders/{folder_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Personal Projects"
}
```

### 폴더 삭제
```http
DELETE /api/folders/{folder_id}
Authorization: Bearer {token}
```

## 대화 API

### 대화 목록 조회
```http
GET /api/conversations/
Authorization: Bearer {token}
```

### 대화 생성
```http
POST /api/conversations/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "New Chat",
  "folder_id": 1
}
```

### 대화 상세 조회
```http
GET /api/conversations/{conversation_id}
Authorization: Bearer {token}
```

### 대화 수정
```http
PUT /api/conversations/{conversation_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "folder_id": 2
}
```

### 대화 삭제
```http
DELETE /api/conversations/{conversation_id}
Authorization: Bearer {token}
```

### 메시지 추가
```http
POST /api/conversations/{conversation_id}/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "role": "user",
  "content": "Hello!",
  "sources": {}
}
```

## 채팅 API

### 채팅 (비스트리밍)
```http
POST /api/chat
Content-Type: application/json

{
  "message": "고양이 사료 추천해줘",
  "temperature": 0.7,
  "max_tokens": 2048,
  "top_k": 5,
  "conversation_id": 1
}
```

**응답**
```json
{
  "response": "고양이 사료 추천 드립니다...",
  "sources": [
    {
      "title": "고양이 사료 가이드",
      "source": "wiki",
      "score": 0.85
    }
  ]
}
```

### 채팅 (스트리밍)
```http
POST /api/chat/stream
Content-Type: application/json

{
  "message": "고양이 사료 추천해줘",
  "temperature": 0.7,
  "max_tokens": 2048,
  "top_k": 5
}
```

**응답** (Server-Sent Events)
```
data: {"type": "sources", "data": [...]}

data: {"type": "token", "data": "고양이"}

data: {"type": "token", "data": " 사료"}

data: {"type": "done"}
```

## 데이터베이스 스키마

### User
- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `password_hash`: String
- `created_at`: DateTime

### Folder
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `name`: String
- `created_at`: DateTime

### Conversation
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `folder_id`: Integer (Foreign Key, Nullable)
- `title`: String
- `created_at`: DateTime
- `updated_at`: DateTime

### Message
- `id`: Integer (Primary Key)
- `conversation_id`: Integer (Foreign Key)
- `role`: String (user/assistant)
- `content`: Text
- `sources`: JSON (Nullable)
- `created_at`: DateTime
