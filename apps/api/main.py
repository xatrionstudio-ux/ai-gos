"""
AI Growth Operating System (AI-GOS) — FastAPI Gateway Application.

Architecture principles:
- Router only: NO business logic in controllers
- Clean Architecture / Hexagonal Architecture
- OpenAPI specifications automatically generated
- Health checks: /health (liveness), /ready (readiness)
- Prometheus metrics: /metrics
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add monorepo package & domain paths to sys.path for cloud deployment compatibility
_root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root_dir))
sys.path.insert(0, str(_root_dir / "packages"))
sys.path.insert(0, str(_root_dir / "domains"))

from fastapi.responses import JSONResponse
try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    _HAS_PROMETHEUS = True
except ImportError:
    CONTENT_TYPE_LATEST = "text/plain"
    def generate_latest(): return b"# prometheus metrics\n"
    _HAS_PROMETHEUS = False
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.exceptions import AIGOSException
from domains.identity.api.auth_router import router as auth_router
from domains.identity.api.dependencies import get_db_session
from domains.projects.api.projects_router import router as projects_router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai-gos-api")

# Database engine & sessionmaker (singleton)
_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_db_url() -> str:
    user = os.getenv("POSTGRES_USER", "aigos")
    pwd = os.getenv("POSTGRES_PASSWORD", "changeme")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "aigos")
    return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan manager for DB engine and background resources."""
    global _engine, _sessionmaker
    logger.info("Initializing database connection pool...")
    db_url = get_db_url()
    _engine = create_async_engine(
        db_url,
        pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
        max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "40")),
        pool_pre_ping=True,
    )
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)

    # Register DB session dependency override
    async def _session_dependency() -> AsyncGenerator[AsyncSession, None]:
        assert _sessionmaker is not None
        async with _sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _session_dependency

    logger.info("AI-GOS API Gateway started successfully.")
    yield

    logger.info("Shutting down database connection pool...")
    if _engine:
        await _engine.dispose()
    logger.info("AI-GOS API Gateway shutdown complete.")


app = FastAPI(
    title="AI Growth Operating System API",
    description="Autonomous multi-tenant platform operating the entire marketing & knowledge lifecycle for SaaS products.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ─── Middleware ───────────────────────────────────────────────────────────────

# CORS
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
origins = [o.strip() for o in origins_str.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Security headers middleware enforcing OWASP recommendations."""
    response: Response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    return response


# ─── Exception Handlers ───────────────────────────────────────────────────────

@app.exception_handler(AIGOSException)
async def domain_exception_handler(request: Request, exc: AIGOSException) -> JSONResponse:
    """Map domain exceptions to standard structured JSON responses."""
    status_map = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "FORBIDDEN": status.HTTP_403_FORBIDDEN,
        "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "RATE_LIMITED": status.HTTP_429_TOO_MANY_REQUESTS,
        "TENANT_ISOLATION_VIOLATION": status.HTTP_403_FORBIDDEN,
    }
    status_code = status_map.get(exc.code, status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")


# ─── System Endpoints ─────────────────────────────────────────────────────────

@app.get("/health", tags=["System"], summary="Liveness probe")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "ai-gos-api"}


@app.get("/ready", tags=["System"], summary="Readiness probe")
async def readiness_check() -> dict[str, Any]:
    # Check DB connection
    db_ok = False
    if _engine:
        try:
            async with _engine.connect() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
                db_ok = True
        except Exception as exc:
            logger.error("Readiness check failed for DB: %s", exc)

    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "db": db_ok},
        )

    return {"status": "ready", "db": db_ok}


@app.get("/metrics", tags=["System"], summary="Prometheus metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
