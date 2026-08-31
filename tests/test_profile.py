import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import app
from backend.app.models.user import User
from backend.app.models.skill import Skill
from backend.app.models.role import Role

client = TestClient(app)


@pytest.fixture
def auth_headers_user_a(db_session):
    """Creates User A and returns auth headers with Bearer token."""
    email = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "User A",
        "email": email,
        "password": "Password123!"
    })
    token = r.json()["data"]["access_token"]
    user_id = uuid.UUID(r.json()["data"]["user"]["id"])
    return {"Authorization": f"Bearer {token}", "user_id": user_id}


@pytest.fixture
def auth_headers_user_b(db_session):
    """Creates User B and returns auth headers with Bearer token."""
    email = f"user_b_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "User B",
        "email": email,
        "password": "Password123!"
    })
    token = r.json()["data"]["access_token"]
    user_id = uuid.UUID(r.json()["data"]["user"]["id"])
    return {"Authorization": f"Bearer {token}", "user_id": user_id}


def test_get_own_profile(auth_headers_user_a):
    """Test 1: Authenticated user can retrieve their own learner profile."""
    headers = {"Authorization": auth_headers_user_a["Authorization"]}
    r = client.get("/api/v1/profile", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["user_id"] == str(auth_headers_user_a["user_id"])


def test_unauthenticated_profile_access_rejected():
    """Test 2: Unauthenticated request to /profile is rejected with 401."""
    r = client.get("/api/v1/profile")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHENTICATED"


def test_update_own_profile(auth_headers_user_a, db_session):
    """Test 3: Update learner profile settings and target role."""
    headers = {"Authorization": auth_headers_user_a["Authorization"]}
    
    # Fetch a seeded role
    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()

    update_payload = {
        "target_role_id": str(role.id),
        "experience_level": "intermediate",
        "daily_study_hours": 3.5,
        "target_duration_weeks": 16,
        "learning_preferences": {"content_types": ["project", "video"], "depth": "rigorous"}
    }
    r = client.put("/api/v1/profile", json=update_payload, headers=headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["target_role"]["id"] == str(role.id)
    assert data["target_role"]["name"] == "AI/ML Engineer"
    assert data["experience_level"] == "intermediate"
    assert data["daily_study_hours"] == 3.5
    assert data["target_duration_weeks"] == 16
    assert data["learning_preferences"]["depth"] == "rigorous"


def test_add_and_get_learner_skills(auth_headers_user_a, db_session):
    """Test 4: Add learner skill and list learner skills."""
    headers = {"Authorization": auth_headers_user_a["Authorization"]}
    
    # Fetch a seeded skill
    python_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()

    add_payload = {
        "skill_id": str(python_skill.id),
        "proficiency": 75.0,
        "source": "self_declared",
        "confidence": 0.9
    }
    r_add = client.post("/api/v1/profile/skills", json=add_payload, headers=headers)
    assert r_add.status_code == 201
    add_data = r_add.json()["data"]
    assert add_data["skill_name"] == "Python"
    assert add_data["proficiency"] == 75.0

    # List learner skills
    r_list = client.get("/api/v1/profile/skills", headers=headers)
    assert r_list.status_code == 200
    skills = r_list.json()["data"]
    assert len(skills) >= 1
    assert any(s["skill_id"] == str(python_skill.id) and s["proficiency"] == 75.0 for s in skills)


def test_duplicate_learner_skill_rejected(auth_headers_user_a, db_session):
    """Test 5: Adding a duplicate skill already in profile returns 409 Conflict."""
    headers = {"Authorization": auth_headers_user_a["Authorization"]}
    sql_skill = db_session.execute(select(Skill).where(Skill.slug == "sql")).scalar_one()

    payload = {
        "skill_id": str(sql_skill.id),
        "proficiency": 60.0,
        "source": "self_declared"
    }
    r1 = client.post("/api/v1/profile/skills", json=payload, headers=headers)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/profile/skills", json=payload, headers=headers)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "CONFLICT"


def test_update_and_delete_learner_skill(auth_headers_user_a, db_session):
    """Test 6: Update proficiency and delete skill from profile."""
    headers = {"Authorization": auth_headers_user_a["Authorization"]}
    git_skill = db_session.execute(select(Skill).where(Skill.slug == "git")).scalar_one()

    # Add
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(git_skill.id),
        "proficiency": 50.0,
        "source": "self_declared"
    }, headers=headers)

    # Update
    r_update = client.put(f"/api/v1/profile/skills/{git_skill.id}", json={
        "proficiency": 85.0,
        "source": "assessment",
        "confidence": 0.95
    }, headers=headers)
    assert r_update.status_code == 200
    assert r_update.json()["data"]["proficiency"] == 85.0

    # Delete
    r_del = client.delete(f"/api/v1/profile/skills/{git_skill.id}", headers=headers)
    assert r_del.status_code == 204

    # Verify deleted
    r_list = client.get("/api/v1/profile/skills", headers=headers)
    assert not any(s["skill_id"] == str(git_skill.id) for s in r_list.json()["data"])


def test_user_data_isolation_between_learners(auth_headers_user_a, auth_headers_user_b, db_session):
    """Test 7: User A cannot see or mutate User B's profile skills."""
    headers_a = {"Authorization": auth_headers_user_a["Authorization"]}
    headers_b = {"Authorization": auth_headers_user_b["Authorization"]}

    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    # User B adds Statistics skill
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(stats_skill.id),
        "proficiency": 80.0
    }, headers=headers_b)

    # User A listing skills must NOT see User B's Statistics skill
    r_a = client.get("/api/v1/profile/skills", headers=headers_a)
    assert not any(s["skill_id"] == str(stats_skill.id) for s in r_a.json()["data"])
