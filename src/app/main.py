"""
FastAPI 메인 애플리케이션
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
import os

from app.core.config import settings
from app.core.exceptions import create_error_response
from app.api.v1.router import api_router
from app.middleware.logging import LoggingMiddleware
from app.middleware.cors_fix import CORBFixMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application...")

    # 시작 시 CORS 설정 확인용 로그
    logger.info(f"CORS origins = {settings.cors_origins_list}")
    logger.info(f"ENV = {getattr(settings, 'ENV', 'unknown')}")

    if os.getenv("TESTING") != "1" and os.getenv("PYTEST_CURRENT_TEST") is None:
        from app.db.session import engine
        try:
            with engine.connect() as conn:
                logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")

    yield
    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Calendar Suite API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Calendar Suite API",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.2"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# -----------------------------
# 미들웨어 순서가 핵심!
# "마지막에 추가한 미들웨어가 가장 바깥(outermost)" 입니다.
# => CORS는 반드시 "가장 마지막"에 추가해야 500/예외 응답에도 CORS 헤더가 붙습니다.
# -----------------------------

# CORB 에러 방지 (OpenAPI JSON용)
app.add_middleware(CORBFixMiddleware)

# Rate Limit (Redis 기반) - OPTIONS는 내부에서 bypass 처리됨 (rate_limit.py 참고)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)

# 로깅
app.add_middleware(LoggingMiddleware)

# Session Middleware (Required for Google OAuth)
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET,
    https_only=False,
    same_site="lax"
)

# ✅ CORS는 반드시 마지막에 추가 (outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # 디버깅 편의(선택)
    max_age=600,
)

# 라우터
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=exc.errors(),
        request=request,
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return create_error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Validation failed",
        details=exc.errors(),
        request=request,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    status_code = exc.status_code
    detail = exc.detail or "An error occurred"
    
    # 기본 코드 매핑
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    
    # 세부 코드 매핑 (메시지 기반)
    code = code_map.get(status_code, f"HTTP_{status_code}")
    
    # 400 계열 세부 구분
    if status_code == 400:
        if "validation" in detail.lower() or "invalid" in detail.lower():
            code = "VALIDATION_FAILED"
        elif "query" in detail.lower() or "parameter" in detail.lower():
            code = "INVALID_QUERY_PARAM"
    
    # 401 계열 세부 구분
    elif status_code == 401:
        if "expired" in detail.lower():
            code = "TOKEN_EXPIRED"
        elif "invalid" in detail.lower() and "token" in detail.lower():
            code = "INVALID_TOKEN"
    
    # 404 계열 세부 구분
    elif status_code == 404:
        if "user" in detail.lower():
            code = "USER_NOT_FOUND"
        elif "calendar" in detail.lower():
            code = "CALENDAR_NOT_FOUND"
        elif "event" in detail.lower():
            code = "EVENT_NOT_FOUND"
        elif "task" in detail.lower():
            code = "TASK_NOT_FOUND"
        else:
            code = "RESOURCE_NOT_FOUND"
    
    # 409 계열 세부 구분
    elif status_code == 409:
        if "duplicate" in detail.lower() or "already" in detail.lower():
            code = "DUPLICATE_RESOURCE"
        elif "state" in detail.lower() or "conflict" in detail.lower():
            code = "STATE_CONFLICT"
    
    # 500 계열 세부 구분
    elif status_code == 500:
        if "database" in detail.lower() or "db" in detail.lower():
            code = "DATABASE_ERROR"
        elif "unknown" in detail.lower():
            code = "UNKNOWN_ERROR"
    
    return create_error_response(
        status_code=status_code,
        code=code,
        message=detail,
        details={},
        request=request,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # stacktrace 로그 남기기
    logger.exception("Unhandled exception")
    return create_error_response(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="An internal server error occurred",
        details={"error": str(exc)},
        request=request,
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION, "buildTime": settings.BUILD_TIME}
