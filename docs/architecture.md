# Architecture Overview

## System Architecture

```
┌────────────────┐       ┌────────────────┐       ┌─────────────────┐
│                │       │                │       │                 │
│    Client      │──────▶│   FastAPI      │──────▶│     MySQL       │
│  (Frontend/    │       │   Application  │       │   (calendar_    │
│   Postman)     │◀──────│                │◀──────│    suite)       │
│                │       │                │       │                 │
└────────────────┘       └────────────────┘       └─────────────────┘
                                │
                                │         ┌─────────────────┐
                                └────────▶│     Redis       │
                                          │   (Cache +      │
                                          │   Rate Limit)   │
                                          └─────────────────┘
```

---

## Application Layers

### 1. Presentation Layer
- **Location**: `app/api/v1/`
- **Responsibility**: HTTP request/response handling, input validation
- **Components**: Routers (`auth.py`, `calendars.py`, `events.py`, `tasks.py`, etc.)

### 2. Business Logic Layer
- **Location**: `app/core/`
- **Responsibility**: Authentication, authorization, security, configuration
- **Components**: 
  - `security.py`: JWT, password hashing
  - `dependencies.py`: Auth middleware
  - `firebase.py`, `google_oauth.py`: Social login
  
### 3. Data Access Layer
- **Location**: `app/models/`, `app/schemas/`
- **Responsibility**: Database ORM models, data validation schemas
- **Components**:
  - Models: `user.py`, `calendar.py`, `event.py`, `task.py`
  - Schemas: Pydantic for request/response validation

### 4. Infrastructure Layer
- **Location**: `app/db/`, `app/middleware/`
- **Responsibility**: Database sessions, Redis, middleware (logging, CORS, rate limiting)

---

## Module Dependency Flow

```
Router (API) → Schema (Validation) → Dependencies (Auth) → 
Business Logic → Models (ORM) → Database
```

---

## Deployment Architecture

### Local Development
```
localhost:8080 → uvicorn → app.main:app
                    ↓
            MySQL (localhost:3306)
            Redis (localhost:6379)
```

### Docker Deployment
```
Docker Compose
├── mysql:8 (port 3307:3306)
├── redis:7-alpine (port 6379:6379)
└── server (FastAPI, port 8080:8080)
    - Build: Dockerfile
    - Volumes: .:/app (dev mode)
    - Env: env_prod.txt
```

### JCloud Production
```
JCloud VM (113.198.66.68)
    ├── Docker Compose (same as above)
    ├── Port Mapping: 10184 → 8080
    └── Health Check: /health
```

---

## Security Layers

1. **Transport Security**: HTTPS (proxy 권장)
2. **Authentication**: JWT (Bearer token)
3. **Authorization**: RBAC (Role-based access control)
4. **Input Validation**: Pydantic schemas
5. **Rate Limiting**: Redis-based throttling
6. **Password Security**: bcrypt hashing

---

## Data Flow Example: Creating an Event

1. **Client** → `POST /api/v1/events` + JWT token
2. **Router** (`events.py`) → Validates auth via `get_current_user` dependency
3. **Schema** (`EventCreate`) → Validates request body
4. **Business Logic** → Checks calendar ownership
5. **ORM** (`Event` model) → Creates DB record
6. **Database** (`calendar_suite.events`) → Persists data
7. **Response** → Returns `EventResponse` (201 Created)
