import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
from collections import defaultdict
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
from backend.app.core.config import settings

# Initialize Argon2 password hasher
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2 hashed password."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access_token"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


class InMemoryRateLimiter:
    """Lightweight in-memory sliding window rate limiter for auth endpoints.
    Does not require Redis or external infrastructure.
    """
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if request for key (e.g. client IP or email) is within rate limit.
        Returns: (is_allowed, seconds_to_wait)
        """
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Clean expired timestamps
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        
        if len(self._requests[key]) >= self.max_requests:
            oldest = self._requests[key][0]
            retry_after = int(self.window_seconds - (now - oldest)) + 1
            return False, max(1, retry_after)
            
        self._requests[key].append(now)
        return True, 0

    def reset(self, key: str):
        """Reset rate limiter state for key."""
        if key in self._requests:
            del self._requests[key]


import hmac

def constant_time_compare(val1: str, val2: str) -> bool:
    """Perform constant-time string comparison to prevent timing attacks."""
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


# Global rate limiter instances (SECURITY_SPEC.md §49)
auth_rate_limiter = InMemoryRateLimiter(max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60)
ai_rate_limiter = InMemoryRateLimiter(max_requests=settings.RATE_LIMIT_AI_PER_MINUTE, window_seconds=60)
roadmap_rate_limiter = InMemoryRateLimiter(max_requests=settings.RATE_LIMIT_ROADMAP_PER_MINUTE, window_seconds=60)

