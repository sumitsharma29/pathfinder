import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import app
from backend.app.models.skill import Skill
from backend.app.models.role import Role

client = TestClient(app)


def test_list_skills_catalog(db_session):
    """Test 1: List all skills in catalog and filter by category."""
    r = client.get("/api/v1/skills")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    skills = data["data"]
    assert len(skills) >= 18
    assert any(s["slug"] == "python" for s in skills)

    # Category filter
    r_math = client.get("/api/v1/skills?category=Mathematics")
    assert r_math.status_code == 200
    math_skills = r_math.json()["data"]
    assert len(math_skills) >= 2
    assert all("mathematics" in s["category"].lower() for s in math_skills)


def test_get_skill_details_and_prerequisites(db_session):
    """Test 2: Retrieve skill details with upstream and downstream dependencies."""
    ml_skill = db_session.execute(select(Skill).where(Skill.slug == "machine-learning")).scalar_one()

    r = client.get(f"/api/v1/skills/{ml_skill.id}")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["name"] == "Machine Learning"
    assert "prerequisites" in data
    assert "dependent_skills" in data

    # Direct prerequisites endpoint
    r_prereqs = client.get(f"/api/v1/skills/{ml_skill.id}/prerequisites")
    assert r_prereqs.status_code == 200
    prereqs = r_prereqs.json()["data"]
    prereq_slugs = [p["prerequisite_skill_slug"] for p in prereqs]
    assert "statistics" in prereq_slugs or "data-processing" in prereq_slugs


def test_invalid_skill_id_returns_404():
    """Test 3: Requesting non-existent skill ID returns 404 NOT_FOUND."""
    fake_id = uuid.uuid4()
    r = client.get(f"/api/v1/skills/{fake_id}")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_list_roles_catalog(db_session):
    """Test 4: List all career roles in catalog."""
    r = client.get("/api/v1/roles")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    roles = data["data"]
    assert len(roles) >= 8
    assert any(r["slug"] == "ai-ml-engineer" for r in roles)


def test_get_role_details_with_required_skills(db_session):
    """Test 5: Retrieve role requirements including all 18 skills for AI/ML Engineer."""
    aiml_role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()

    r = client.get(f"/api/v1/roles/{aiml_role.id}")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["name"] == "AI/ML Engineer"
    assert len(data["required_skills"]) == 18

    # Specific required skills endpoint
    r_skills = client.get(f"/api/v1/roles/{aiml_role.id}/skills")
    assert r_skills.status_code == 200
    req_skills = r_skills.json()["data"]
    assert len(req_skills) == 18
    python_req = next((s for s in req_skills if s["skill_slug"] == "python"), None)
    assert python_req is not None
    assert python_req["required_proficiency"] == 80.0
    assert python_req["importance"] == 1.0


def test_invalid_role_id_returns_404():
    """Test 6: Requesting non-existent role ID returns 404 NOT_FOUND."""
    fake_id = uuid.uuid4()
    r = client.get(f"/api/v1/roles/{fake_id}")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"
