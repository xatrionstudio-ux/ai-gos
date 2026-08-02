"""
JWT service for RS256 token generation and verification.

Security guarantees:
- RS256 algorithm hardcoded — 'none' algorithm always rejected
- Private key loaded from filesystem path (never from env string)
- Access tokens: 15-minute TTL
- Refresh tokens: 30-day TTL, stored as SHA-256 hash in DB
- 'exp' claim validated on every decode
- Audience and issuer claims included and validated

TODO(security): Implement token binding (DPoP) for enhanced security
  against token theft in high-security deployments.
"""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

logger = logging.getLogger(__name__)

_ALGORITHM = "RS256"  # Hardcoded — never allow algorithm override from token header
_ISSUER = "ai-gos"
_AUDIENCE = "ai-gos-api"
_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))


def _load_private_key() -> RSAPrivateKey:
    """Load RSA private key from filesystem. Fails loudly if missing."""
    key_path = Path(os.environ.get("JWT_PRIVATE_KEY_PATH", "infrastructure/keys/jwt_private.pem"))
    if not key_path.exists():
        raise RuntimeError(
            f"JWT private key not found at {key_path}. "
            "Run 'make keys' to generate the RS256 key pair."
        )
    with key_path.open("rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)  # type: ignore


def _load_public_key() -> RSAPublicKey:
    """Load RSA public key from filesystem."""
    key_path = Path(os.environ.get("JWT_PUBLIC_KEY_PATH", "infrastructure/keys/jwt_public.pem"))
    if not key_path.exists():
        raise RuntimeError(
            f"JWT public key not found at {key_path}. "
            "Run 'make keys' to generate the RS256 key pair."
        )
    with key_path.open("rb") as f:
        return serialization.load_pem_public_key(f.read())  # type: ignore


class TokenPayload:
    """Typed access token payload."""

    def __init__(
        self,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        email: str,
        is_superuser: bool,
        permissions: list[str],
    ) -> None:
        self.user_id = user_id
        self.org_id = org_id
        self.email = email
        self.is_superuser = is_superuser
        self.permissions = permissions


class JWTService:
    """
    RS256 JWT token service.

    Provides access token creation, refresh token generation (opaque),
    and token verification with full claim validation.
    """

    def __init__(self) -> None:
        self._private_key = _load_private_key()
        self._public_key = _load_public_key()

    def create_access_token(
        self,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        email: str,
        is_superuser: bool,
        permissions: list[str],
    ) -> str:
        """Create a short-lived JWT access token."""
        now = datetime.now(UTC)
        payload = {
            # Standard JWT claims
            "iss": _ISSUER,
            "aud": _AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES),
            "jti": str(uuid.uuid4()),
            # Application claims
            "sub": str(user_id),
            "org_id": str(org_id),
            "email": email,
            "is_superuser": is_superuser,
            "permissions": permissions,
        }
        return jwt.encode(payload, self._private_key, algorithm=_ALGORITHM)

    def create_refresh_token(self) -> tuple[str, str]:
        """
        Create an opaque refresh token.

        Returns: (raw_token, token_hash)
        - raw_token: 256-bit cryptographically random hex string
        - token_hash: SHA-256 hash for DB storage (NEVER store raw)
        """
        raw_token = secrets.token_hex(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        return raw_token, token_hash

    def hash_refresh_token(self, raw_token: str) -> str:
        """Hash a refresh token for DB lookup."""
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def decode_access_token(self, token: str) -> TokenPayload:
        """
        Decode and validate an access token.

        Raises jwt.ExpiredSignatureError, jwt.InvalidTokenError on failure.
        NEVER accept 'none' algorithm — RS256 is hardcoded.
        """
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=[_ALGORITHM],  # Hardcoded allowlist — never from token header
                issuer=_ISSUER,
                audience=_AUDIENCE,
                options={
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "require": ["exp", "iat", "sub", "org_id", "jti"],
                },
            )
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise
        except Exception as exc:
            logger.exception("Unexpected JWT decode error")
            raise jwt.InvalidTokenError("Token validation failed.") from exc

        return TokenPayload(
            user_id=uuid.UUID(payload["sub"]),
            org_id=uuid.UUID(payload["org_id"]),
            email=payload["email"],
            is_superuser=payload.get("is_superuser", False),
            permissions=payload.get("permissions", []),
        )

    def get_token_expiry(self) -> timedelta:
        return timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES)

    def get_refresh_expiry(self) -> timedelta:
        return timedelta(days=_REFRESH_TOKEN_EXPIRE_DAYS)
