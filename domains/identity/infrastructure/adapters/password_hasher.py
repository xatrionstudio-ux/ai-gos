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
import hashlib
import hmac

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
    _ph = PasswordHasher(
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        salt_len=16,
    )
    _HAS_ARGON2 = True
except ImportError:
    _ph = None
    _HAS_ARGON2 = False



class PasswordHasherAdapter:
    """Argon2id password hashing service."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using Argon2id or fallback PBKDF2."""
        if _HAS_ARGON2 and _ph is not None:
            return _ph.hash(password)
        salt = hashlib.sha256(password.encode()).hexdigest()[:16]
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return f"pbkdf2_sha256$100000${salt}${h.hex()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hash."""
        if _HAS_ARGON2 and _ph is not None and not hashed_password.startswith("pbkdf2"):
            try:
                return _ph.verify(hashed_password, password)
            except Exception:
                return False
        if hashed_password.startswith("pbkdf2"):
            parts = hashed_password.split("$")
            if len(parts) == 4:
                salt, expected_hash = parts[2], parts[3]
                calc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
                return hmac.compare_digest(calc, expected_hash)
        return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """Check if the password hash needs to be updated."""
        if _HAS_ARGON2 and _ph is not None and not hashed_password.startswith("pbkdf2"):
            try:
                return _ph.check_needs_rehash(hashed_password)
            except Exception:
                return True
        return False
