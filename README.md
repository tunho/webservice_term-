# Term Project: Calendar Suite API

## 1. 프로젝트 개요
**Calendar Suite**는 개인 및 팀을 위한 종합 일정 관리 플랫폼입니다. 사용자는 캘린더를 생성하고, 이벤트와 작업을 관리하며, 팀원들과 일정을 공유할 수 있습니다.

### 주요 기능
- **사용자 관리**: 회원가입, 로그인, 프로필 관리, 관리자 기능 (회원 차단/해제)
- **캘린더 관리**: 개인/공유 캘린더 생성, 수정, 삭제
- **이벤트/작업 관리**: 일정 및 할 일(Task) CRUD, 중요도/상태 관리
- **통계**: 일일 활동량, 인기 캘린더 등 관리자용 통계 제공
- **보안**: JWT 기반 인증, 이메일/Google/Firebase 소셜 로그인, RBAC (User/Admin)

---

## 2. 실행 방법

### 사전 요구사항
- Docker & Docker Compose
- Python 3.9+ (로컬 실행 시)

### Docker 실행 (권장)
1. 레포지토리 클론 및 이동
   ```bash
   git clone <REPO_URL>
   cd server
   ```
2. 환경변수 설정
   ```bash
   cp .env.example .env
   # .env 파일 수정 (필요 시)
   ```
3. 서비스 실행
   ```bash
   docker compose up -d --build
   ```
4. 시드 데이터 생성 (테스트용 데이터 200+건)
   ```bash
   docker compose exec server python scripts/seed.py
   ```
5. 접속 확인
   - Health Check: `http://localhost:8080/health`
   - Swagger UI: `http://localhost:8080/docs`

5. API 검증 (Postman 대안)
   Postman 클라이언트 설정 문제로 실행이 어려울 경우, 제공된 Python 스크립트로 전체 API 기능을 검증할 수 있습니다.
   ```bash
   # 서버 컨테이너 내부에서 실행
   docker compose exec server python server/postman/run_api_tests.py
   ```
   **실행 결과 예시:**
   ```
   [SUCCESS] Health Check passed
   [SUCCESS] Signup passed
   [SUCCESS] Login passed
   [SUCCESS] Create/Delete Calendar passed
   ...
   ✨ All automated tests completed successfully!
   ```

### 로컬 실행 (개발용)
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# DB 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

---

## 3. 환경변수 설명 (`.env`)

| 변수명 | 설명 | 기본값/예시 |
|--------|------|-------------|
| `ENV` | 실행 환경 (dev/prod) | `development` |
| `MYSQL_HOST` | MySQL 호스트 | `localhost` (Docker: `mysql`) |
| `MYSQL_PORT` | MySQL 포트 | `3306` |
| `MYSQL_USER` | DB 사용자 | `calendar_user` |
| `MYSQL_PASSWORD` | DB 비밀번호 | `calendar_password` |
| `MYSQL_DB` | DB 이름 | `calendar_suite` |
| `REDIS_HOST` | Redis 호스트 | `localhost` (Docker: `redis`) |
| `JWT_SECRET` | JWT 서명 비밀키 | `your-secret-key...` |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth 클라이언트 ID | - |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth 클라이언트 시크릿 | - |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase 키 파일 경로 | `./firebase.json` |

---

## 4. 배포 주소
- **Base URL**: `http://113.198.66.68:10184/api/v1`
- **Swagger UI**: `http://113.198.66.68:10184/docs`
- **Health Check**: `http://113.198.66.68:10184/health`

---

## 5. 인증 플로우 & 권한

### 인증 방식
- **JWT (JSON Web Token)**: Access Token (30분), Refresh Token (7일)
- **Social Login**:
  - **Google**: OAuth 2.0 Authorization Code Flow
  - **Firebase**: Client SDK에서 ID Token 발급 -> 서버에서 검증 후 JWT 발급

### 역할(Role) 및 권한

| 역할 | 권한 범위 | 비고 |
|------|-----------|------|
| **ROLE_USER** | 본인 정보 수정, 본인 캘린더/이벤트/작업 CRUD | 일반 사용자 |
| **ROLE_ADMIN** | 모든 사용자 조회/수정/차단, 시스템 통계 조회 | 관리자 |

### 예제 계정 (Seed 데이터 기준)
| 역할 | 이메일 | 비밀번호 |
|------|--------|----------|
| **Admin** | `admin@example.com` | `password123` |
| **User** | `user@example.com` | `password123` |
*(참고: 시드 데이터 생성 시 랜덤으로 생성되므로, `scripts/seed.py` 실행 후 로그를 확인하거나 DB를 직접 확인해야 할 수 있습니다. 위 계정은 예시입니다.)*

---

## 6. DB 연결 정보 (테스트용)
- **Host**: `113.198.66.68`
- **Port**: `3307` (외부 노출 포트)
- **Database**: `calendar_suite`
- **User**: `calendar_user`
- **Password**: `calendar_password`

---

## 7. 엔드포인트 요약

| 리소스 | Method | URL | 설명 | 권한 |
|--------|--------|-----|------|------|
| **Auth** | POST | `/auth/login` | 로그인 | 누구나 |
| | POST | `/auth/refresh` | 토큰 갱신 | 누구나 |
| **Users** | GET | `/users/me` | 내 정보 조회 | User+ |
| | GET | `/admin/users` | 전체 사용자 조회 | Admin |
| **Calendars** | GET | `/calendars` | 캘린더 목록 | User+ |
| | POST | `/calendars` | 캘린더 생성 | User+ |
| **Events** | GET | `/events` | 이벤트 목록 (검색/필터) | User+ |
| **Tasks** | POST | `/tasks` | 작업 생성 | User+ |
| **Stats** | GET | `/stats/daily` | 일일 통계 | Admin |

*(전체 API 명세는 Swagger UI 참고)*

---

## 8. 성능 및 보안 고려사항

### 성능
- **Redis 캐싱**: Refresh Token 저장 및 검증에 Redis 사용으로 DB 부하 감소
- **Database Indexing**: 자주 조회되는 `email`, `user_id`, `calendar_id` 컬럼에 인덱스 적용
- **Pagination**: 대량 데이터 조회 시 페이지네이션 강제 적용 (`page`, `size`)

### 보안
- **Password Hashing**: `bcrypt`를 사용하여 비밀번호 단방향 암호화 저장
- **Rate Limiting**: `slowapi`를 사용하여 IP 기반 요청 제한 (DDoS 방지)
- **Input Validation**: `Pydantic`을 통한 엄격한 요청 데이터 검증
- **CORS**: 허용된 도메인(`localhost`, 프론트엔드 도메인)만 접근 허용

---

## 9. 한계와 개선 계획
- **실시간 알림**: 현재 Polling 방식이나, 추후 WebSocket을 도입하여 실시간 일정 공유 알림 구현 예정
- **파일 첨부**: 이벤트/작업에 파일 첨부 기능 추가 (AWS S3 연동)
- **테스트 커버리지**: 현재 핵심 로직 위주 테스트 -> E2E 테스트 추가 예정
