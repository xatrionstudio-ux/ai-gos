"""
Argon2id password hashing adapter.

Uses argon2-cffi with recommended OWASP parameters:
- Time cost (iterations): 3
- Memory cost: 65536 KiB (64 MiB)
- Parallelism: 4
- Salt length: 16 bytes
- Hash length: 32 bytes
"""

from __future__ import annotations

import logging
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

logger = logging.getLogger(__name__)

# OWASP recommended parameters for Argon2id
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


class PasswordHasherAdapter:
    """Argon2id password hashing service."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using Argon2id."""
        return _ph.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against an Argon2id hash."""
        try:
            return _ph.verify(hashed_password, password)
        except (VerificationError, VerifyMismatchError, InvalidHashError):
            return False
        except Exception:
            logger.exception("Unexpected error verifying password hash")
            return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """Check if the password hash needs to be updated to match current parameters."""
        try:
            return _ph.check_needs_rehash(hashed_password)
        except Exception:
            return True
