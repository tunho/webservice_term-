# API Design & Changes from Assignment 1

## Comparison with Assignment 1

### What Changed
1. **Authentication**: 
   - **Before**: Basic username/password (과제1)
   - **After**: JWT + Google OAuth + Firebase Auth (과제2)

2. **Authorization**:
   - **Before**: 단순 로그인/로그아웃
   - **After**: RBAC with ROLE_USER and ROLE_ADMIN

3. **Endpoints**:
   - **Before**: ~15 endpoints (간단한 CRUD)
   - **After**: 40+ endpoints (검색, 필터, 통계, 관리자 기능 추가)

4. **Validation**:
   - **Before**: 기본 타입 검증
   - **After**: Pydantic schemas로 엄격한 검증

5. **Error Handling**:
   - **Before**: 단순 HTTP 에러
   - **After**: 12+ 표준화된 에러 코드

6. **Database**:
   - **Before**: SQLite (개발용)
   - **After**: MySQL + Redis (프로덕션)

7. **Deployment**:
   - **Before**: 로컬 실행만
   - **After**: Docker + JCloud 배포

---

## Design Decisions

### 1. Why JWT over Session?
- **Scalability**: Stateless 인증으로 수평 확장 가능
- **Mobile Support**: 토큰 기반이라 모바일 앱에도 적합
- **Decoupling**: Auth 서버와 API 서버 분리 가능

### 2. Why Redis?
- **Session Storage**: Refresh Token을 DB 대신 Redis에 저장 (빠른 조회)
- **Rate Limiting**: IP별 요청 제한 (DDoS 방지)
- **Cache**: 향후 자주 조회되는 데이터 캐싱 가능

### 3. Why Pagination?
- **Performance**: 대량 데이터 조회 시 메모리 효율
- **UX**: 프론트엔드에서 무한 스크롤/페이지 네비게이션 구현 가능

### 4. Why RBAC (Role-Based Access Control)?
- **Security**: 관리자 기능 보호 (통계, 사용자 관리)
- **Extensibility**: 향후 ROLE_MANAGER, ROLE_VIEWER 등 확장 가능

---

## API Versioning Strategy

현재: `/api/v1/...`

향후 `/api/v2/` 추가 시:
- v1은 deprecated 처리하되 유지 (하위 호환)
- v2에서 breaking changes 적용

---

## Response Format

### Success Response
```json
{
  "id": "uuid",
  "title": "Meeting",
  ...
}
```

### Error Response
```json
{
  "timestamp": "2025-03-05T12:00:00Z",
  "path": "/api/v1/events/123",
  "status": 404,
  "code": "EVENT_NOT_FOUND",
  "message": "Event not found",
  "details": {}
}
```

---

## Rate Limiting Policy

- **General**: 60 requests/minute per IP
- **Auth**: 10 login attempts/minute per IP
- **Admin**: 100 requests/minute (더 높은 한도)

---

## Pagination Format

### Request
```
GET /events?page=0&size=20&sort=start_at,DESC
```

### Response
```json
{
  "content": [...],
  "page": 0,
  "size": 20,
  "totalElements": 153,
  "totalPages": 8,
  "sort": "start_at,DESC"
}
```
