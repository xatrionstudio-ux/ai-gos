"""
FastAPI router for Authentication endpoints.

Thin routing layer — delegates all business logic to AuthService.
Handles HTTP status codes, cookies, and request/response validation.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.result import Err, Ok
from domains.identity.application.auth_service import AuthService, LoginCommand, RegisterCommand
from domains.identity.infrastructure.adapters.jwt_service import JWTService
from domains.identity.infrastructure.repositories.user_repository import (
    OrganizationRepository,
    RefreshTokenRepository,
    UserRepository,
)
from domains.identity.api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


# ─── Request / Response Schemas ───────────────────────────────────────────────

class RegisterRequest(BaseModel):
    org_name: str = Field(..., min_length=2, max_length=100)
    org_slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    org_slug: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_id: str
    org_id: str


# ─── Helper Dependency ────────────────────────────────────────────────────────

async def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    user_repo = UserRepository(session)
    org_repo = OrganizationRepository(session)
    token_repo = RefreshTokenRepository(session)
    jwt_service = JWTService()
    return AuthService(user_repo, org_repo, token_repo, jwt_service)


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new organization and owner account",
)
async def register(
    req: RegisterRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    cmd = RegisterCommand(
        org_name=req.org_name,
        org_slug=req.org_slug,
        email=req.email,
        password=req.password,
        full_name=req.full_name,
    )
    result = await service.register_organization_and_owner(cmd)

    if isinstance(result, Ok):
        org, user, tokens = result.value
        # Set secure refresh token cookie
        response.set_cookie(
            key="__Host-refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 86400,
            path="/api/v1/auth",
        )
        return AuthResponse(
            access_token=tokens.access_token,
            expires_in=tokens.expires_in_seconds,
            user_id=str(tokens.user_id),
            org_id=str(tokens.org_id),
        )
    elif isinstance(result, Err):
        error = result.error
        raise HTTPException(
            status_code=getattr(error, "status_code", 400),
            detail=error.to_dict() if hasattr(error, "to_dict") else str(error),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate with email and password",
)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    cmd = LoginCommand(
        org_slug=req.org_slug,
        email=req.email,
        password=req.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    result = await service.login(cmd)

    if isinstance(result, Ok):
        user, tokens = result.value
        response.set_cookie(
            key="__Host-refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 86400,
            path="/api/v1/auth",
        )
        return AuthResponse(
            access_token=tokens.access_token,
            expires_in=tokens.expires_in_seconds,
            user_id=str(tokens.user_id),
            org_id=str(tokens.org_id),
        )
    elif isinstance(result, Err):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."},
        )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token using refresh token",
)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    cookie_token: Annotated[str | None, Cookie(alias="__Host-refresh_token")] = None,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    raw_token = cookie_token or (body.refresh_token if body else None)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Refresh token is required."},
        )

    result = await service.refresh_tokens(
        raw_refresh_token=raw_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    if isinstance(result, Ok):
        tokens = result.value
        response.set_cookie(
            key="__Host-refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 86400,
            path="/api/v1/auth",
        )
        return AuthResponse(
            access_token=tokens.access_token,
            expires_in=tokens.expires_in_seconds,
            user_id=str(tokens.user_id),
            org_id=str(tokens.org_id),
        )
    elif isinstance(result, Err):
        error = result.error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error.to_dict() if hasattr(error, "to_dict") else str(error),
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Revoke refresh token and logout",
)
async def logout(
    response: Response,
    body: RefreshTokenRequest | None = None,
    cookie_token: Annotated[str | None, Cookie(alias="__Host-refresh_token")] = None,
    service: AuthService = Depends(get_auth_service),
) -> None:
    raw_token = cookie_token or (body.refresh_token if body else None)
    if raw_token:
        await service.logout(raw_token)

    response.delete_cookie(key="__Host-refresh_token", path="/api/v1/auth")
