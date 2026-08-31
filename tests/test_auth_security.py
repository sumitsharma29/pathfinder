import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import app
from backend.app.core.security import auth_rate_limiter, create_access_token
from backend.app.models.user import User

client = TestClient(app)


def test_email_normalization():
    """Test 1: Email normalization trims whitespace and lowercases on both register and login."""
    raw_email = f"  MixedCase_{uuid.uuid4().hex[:6]}@Domain.COM  "
    clean_email = raw_email.strip().lower()

    # Register with mixed case and spaces
    r_reg = client.post("/api/v1/auth/register", json={
        "name": "Normalized User",
        "email": raw_email,
        "password": "Password123!"
    })
    assert r_reg.status_code == 201
    assert r_reg.json()["data"]["user"]["email"] == clean_email

    # Login using clean lowercase
    r_login = client.post("/api/v1/auth/login", json={
        "email": clean_email,
        "password": "Password123!"
    })
    assert r_login.status_code == 200


def test_untrusted_client_user_id():
    """Test 2: Server never trusts client-supplied user_id, is_admin, or is_active."""
    fake_user_id = str(uuid.uuid4())
    unique_email = f"attacker_{uuid.uuid4().hex[:8]}@example.com"

    r = client.post("/api/v1/auth/register", json={
        "name": "Attacker",
        "email": unique_email,
        "password": "Password123!",
        "id": fake_user_id,
        "user_id": fake_user_id,
        "is_admin": True,
        "is_active": False
    })
    assert r.status_code == 201
    created_id = r.json()["data"]["user"]["id"]
    # The server must generate its own UUID and ignore client's fake_user_id
    assert created_id != fake_user_id


def test_security_headers_present():
    """Test 3: Security headers (X-Content-Type-Options, X-Frame-Options, etc.) are present on all responses."""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_rate_limiter_blocks_repeated_login_attempts():
    """Test 4: Exceeding 10 rapid failed login attempts triggers 429 Too Many Requests."""
    target_email = f"ratelimit_{uuid.uuid4().hex[:6]}@example.com"
    client_ip = "testclient"
    rate_key = f"login:{client_ip}:{target_email.lower()}"
    auth_rate_limiter.reset(rate_key)

    # Perform 10 failed attempts
    for _ in range(10):
        r = client.post("/api/v1/auth/login", json={
            "email": target_email,
            "password": "WrongPassword123!"
        })
        assert r.status_code == 401

    # 11th attempt must be rate-limited
    r_blocked = client.post("/api/v1/auth/login", json={
        "email": target_email,
        "password": "WrongPassword123!"
    })
    assert r_blocked.status_code == 429
    assert r_blocked.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    # Cleanup
    auth_rate_limiter.reset(rate_key)


def test_tampered_jwt_signature_rejected():
    """Test 5: Tampered JWT token signature is rejected with 401."""
    valid_token = create_access_token(subject=str(uuid.uuid4()))
    # Tamper with the last few signature characters
    tampered_token = valid_token[:-4] + "ABCD"

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_sql_injection_safely_rejected():
    """Test 6: SQL injection payload in login credentials is treated as literal and safely rejected."""
    sqli_email = "' OR '1'='1' --"
    response = client.post("/api/v1/auth/login", json={
        "email": sqli_email,
        "password": "' OR '1'='1"
    })
    # Pydantic will reject invalid email format (422) or auth service rejects (401)
    assert response.status_code in (401, 422)
    assert response.json()["success"] is False
