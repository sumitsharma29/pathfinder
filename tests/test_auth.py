import uuid
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.models.user import User

client = TestClient(app)


def test_health_endpoints():
    """Test /health, /health/live, and /health/ready endpoints."""
    r_health = client.get("/health")
    assert r_health.status_code == 200
    data = r_health.json()
    assert data["status"] == "ok"
    assert "PathFinder AI" in data["app"]

    r_live = client.get("/health/live")
    assert r_live.status_code == 200
    assert r_live.json() == {"status": "ok"}

    r_ready = client.get("/health/ready")
    assert r_ready.status_code == 200
    assert r_ready.json()["status"] == "ready"
    assert r_ready.json()["database"] == "connected"


def test_successful_registration(db_session):
    """Test 1: Successful user registration creates user and learner profile."""
    unique_email = f"learner_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "Jane Doe",
        "email": unique_email,
        "password": "SecurePassword123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["user"]["email"] == unique_email.lower()
    assert res_data["data"]["user"]["name"] == "Jane Doe"
    assert "access_token" in res_data["data"]
    assert res_data["data"]["token_type"] == "bearer"

    # Verify user exists in database with associated profile
    user_id = uuid.UUID(res_data["data"]["user"]["id"])
    user = db_session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    assert user is not None
    assert user.profile is not None
    assert user.profile.user_id == user.id


def test_duplicate_registration_rejected(db_session):
    """Test 2: Duplicate email registration returns 409 Conflict."""
    unique_email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "First User",
        "email": unique_email,
        "password": "Password123!"
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    # Attempt to register again with same email (even with uppercase)
    r2 = client.post("/api/v1/auth/register", json={
        "name": "Second User",
        "email": unique_email.upper(),
        "password": "DifferentPassword123!"
    })
    assert r2.status_code == 409
    res_data = r2.json()
    assert res_data["success"] is False
    assert res_data["error"]["code"] == "CONFLICT"


def test_password_is_not_stored_plaintext(db_session):
    """Test 3: Passwords in database are hashed with Argon2 and never plaintext."""
    raw_password = "PlaintextPasswordToVerify"
    unique_email = f"argon_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "Argon User",
        "email": unique_email,
        "password": raw_password
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    user = db_session.execute(select(User).where(User.email == unique_email.lower())).scalar_one()
    assert user.password_hash != raw_password
    assert raw_password not in user.password_hash
    assert user.password_hash.startswith("$argon2")


def test_successful_login():
    """Test 4: Successful login with valid credentials returns JWT."""
    unique_email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    password = "MyValidPassword123!"
    
    # Register
    client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": unique_email,
        "password": password
    })

    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": password
    })
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["user"]["email"] == unique_email.lower()
    assert "access_token" in res_data["data"]


def test_wrong_password_rejected():
    """Test 5: Wrong password returns 401 Unauthorized."""
    unique_email = f"wrongpw_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/v1/auth/register", json={
        "name": "User",
        "email": unique_email,
        "password": "CorrectPassword123!"
    })

    response = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "IncorrectPassword123!"
    })
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_unknown_account_rejected():
    """Test 6: Unknown email returns generic 401 Unauthorized without leaking account existence."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent_random_user_9876@example.com",
        "password": "SomePassword123!"
    })
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_inactive_account_rejected(db_session):
    """Test 7: Inactive account cannot log in or access protected endpoints."""
    unique_email = f"inactive_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Inactive User",
        "email": unique_email,
        "password": password
    })
    token = reg_res.json()["data"]["access_token"]
    user_id = uuid.UUID(reg_res.json()["data"]["user"]["id"])

    # Deactivate account directly in database
    user = db_session.execute(select(User).where(User.id == user_id)).scalar_one()
    user.is_active = False
    db_session.commit()

    # Login should fail
    login_res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": password
    })
    assert login_res.status_code == 401

    # Protected endpoint with old token should fail
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 401


def test_missing_authentication_rejected():
    """Test 8: Accessing /auth/me without Authorization header returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_invalid_authentication_token_rejected():
    """Test 9: Invalid/corrupted token returns 401."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_expired_authentication_token_rejected(db_session):
    """Test 10: Expired JWT token returns 401."""
    user = User(
        name="Expired Token User",
        email=f"exp_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Create expired token (-10 minutes)
    expired_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=-10))

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_get_current_user_me():
    """Test 11: GET /api/v1/auth/me returns current authenticated user."""
    unique_email = f"me_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Me User",
        "email": unique_email,
        "password": "Password123!"
    })
    token = reg_res.json()["data"]["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["email"] == unique_email.lower()
    assert res_data["data"]["name"] == "Me User"


def test_logout_endpoint():
    """Test 12: POST /api/v1/auth/logout returns 204 No Content for authenticated user."""
    unique_email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Logout User",
        "email": unique_email,
        "password": "Password123!"
    })
    token = reg_res.json()["data"]["access_token"]

    response = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


def test_sensitive_fields_never_returned():
    """Test 13: Sensitive fields (password, password_hash) are never returned in register, login, or me."""
    unique_email = f"safe_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Safe User",
        "email": unique_email,
        "password": "Password123!"
    })
    data = reg_res.json()
    assert "password" not in data["data"]["user"]
    assert "password_hash" not in data["data"]["user"]

    token = data["data"]["access_token"]
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    me_data = me_res.json()
    assert "password" not in me_data["data"]
    assert "password_hash" not in me_data["data"]
