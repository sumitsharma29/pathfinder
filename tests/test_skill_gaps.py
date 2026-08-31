import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from backend.app.main import app
from backend.app.models.skill import Skill
from backend.app.models.role import Role

client = TestClient(app)


@pytest.fixture
def auth_learner_with_aiml_role(db_session):
    """Creates a registered learner and sets their target role to AI/ML Engineer."""
    email = f"gap_learner_{uuid.uuid4().hex[:8]}@example.com"
    r_reg = client.post("/api/v1/auth/register", json={
        "name": "Gap Learner",
        "email": email,
        "password": "Password123!"
    })
    token = r_reg.json()["data"]["access_token"]
    user_id = uuid.UUID(r_reg.json()["data"]["user"]["id"])
    headers = {"Authorization": f"Bearer {token}"}

    # Assign AI/ML Engineer role
    aiml_role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()
    client.put("/api/v1/profile", json={"target_role_id": str(aiml_role.id)}, headers=headers)

    return {
        "headers": headers,
        "user_id": user_id,
        "role_id": aiml_role.id
    }


def test_missing_skill_gap(auth_learner_with_aiml_role, db_session):
    """Test 1 & 5: When learner has no skill record, current is 0, gap equals required, status is MISSING."""
    headers = auth_learner_with_aiml_role["headers"]
    
    r = client.get("/api/v1/skill-gaps", headers=headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["target_role"] == "AI/ML Engineer"
    assert data["summary"]["total_skills_required"] == 18
    assert data["summary"]["skills_missing"] == 18
    assert data["summary"]["overall_readiness_percentage"] == 0.0

    python_item = next(s for s in data["skills"] if s["skill_slug"] == "python")
    assert python_item["required"] == 80.0
    assert python_item["current"] == 0.0
    assert python_item["gap"] == 80.0
    assert python_item["status"] == "MISSING"


def test_partial_skill_gap(auth_learner_with_aiml_role, db_session):
    """Test 2: When learner has partial proficiency (e.g. 40 on 80 req), gap is 40 and status is PARTIAL."""
    headers = auth_learner_with_aiml_role["headers"]
    python_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()

    # Set Python = 40.0
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(python_skill.id),
        "proficiency": 40.0
    }, headers=headers)

    r = client.get("/api/v1/skill-gaps", headers=headers)
    assert r.status_code == 200
    data = r.json()["data"]
    python_item = next(s for s in data["skills"] if s["skill_slug"] == "python")
    assert python_item["required"] == 80.0
    assert python_item["current"] == 40.0
    assert python_item["gap"] == 40.0
    assert python_item["status"] == "PARTIAL"


def test_exact_and_above_mastery(auth_learner_with_aiml_role, db_session):
    """Test 3 & 4: Exact mastery (80/80) and exceeding requirement (95/80) yield 0 gap and MASTERED status."""
    headers = auth_learner_with_aiml_role["headers"]
    python_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    sql_skill = db_session.execute(select(Skill).where(Skill.slug == "sql")).scalar_one()

    # Python exact mastery (80)
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(python_skill.id),
        "proficiency": 80.0
    }, headers=headers)

    # SQL above requirement (95 > 65)
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(sql_skill.id),
        "proficiency": 95.0
    }, headers=headers)

    r = client.get("/api/v1/skill-gaps", headers=headers)
    assert r.status_code == 200
    data = r.json()["data"]

    python_item = next(s for s in data["skills"] if s["skill_slug"] == "python")
    assert python_item["gap"] == 0.0
    assert python_item["status"] == "MASTERED"

    sql_item = next(s for s in data["skills"] if s["skill_slug"] == "sql")
    assert sql_item["gap"] == 0.0
    assert sql_item["status"] == "MASTERED"


def test_dynamic_proficiency_update_immediately_alters_gaps(auth_learner_with_aiml_role, db_session):
    """Test 7: Updating learner skill immediately changes gap calculation on next request with zero cache lag."""
    headers = auth_learner_with_aiml_role["headers"]
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    # Initial: Statistics = 35 (Req 75 -> Gap 40)
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(stats_skill.id),
        "proficiency": 35.0
    }, headers=headers)

    r1 = client.get("/api/v1/skill-gaps", headers=headers)
    stats1 = next(s for s in r1.json()["data"]["skills"] if s["skill_slug"] == "statistics")
    assert stats1["gap"] == 40.0
    assert stats1["status"] == "PARTIAL"

    # Update Statistics to 80 (Req 75 -> Gap 0, MASTERED)
    client.put(f"/api/v1/profile/skills/{stats_skill.id}", json={
        "proficiency": 80.0
    }, headers=headers)

    r2 = client.get("/api/v1/skill-gaps", headers=headers)
    stats2 = next(s for s in r2.json()["data"]["skills"] if s["skill_slug"] == "statistics")
    assert stats2["gap"] == 0.0
    assert stats2["status"] == "MASTERED"


def test_role_change_alters_gaps_immediately(auth_learner_with_aiml_role, db_session):
    """Test 6: Changing target role immediately evaluates against the new role's requirements."""
    headers = auth_learner_with_aiml_role["headers"]
    ds_role = db_session.execute(select(Role).where(Role.slug == "data-scientist")).scalar_one()

    # Change target role to Data Scientist
    client.put("/api/v1/profile", json={"target_role_id": str(ds_role.id)}, headers=headers)

    r = client.get("/api/v1/skill-gaps", headers=headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["target_role"] == "Data Scientist"
    assert data["target_role_id"] == str(ds_role.id)


def test_prerequisite_awareness_and_priority_calculation(auth_learner_with_aiml_role, db_session):
    """Test 8 & 9: Gap items include prerequisite skill names and priority calculation."""
    headers = auth_learner_with_aiml_role["headers"]
    r = client.get("/api/v1/skill-gaps", headers=headers)
    assert r.status_code == 200
    skills = r.json()["data"]["skills"]

    ml_item = next(s for s in skills if s["skill_slug"] == "machine-learning")
    assert "Statistics" in ml_item["prerequisites"] or "Data Processing" in ml_item["prerequisites"]
    assert ml_item["priority"] > 0


def test_determinism_and_no_persisted_skill_gaps_table(auth_learner_with_aiml_role, db_session):
    """Test 10 & 11: Skill gap engine is 100% deterministic and no static skill_gaps table exists."""
    headers = auth_learner_with_aiml_role["headers"]

    # Multiple calls return identical payloads
    r1 = client.get("/api/v1/skill-gaps", headers=headers).json()
    r2 = client.get("/api/v1/skill-gaps", headers=headers).json()
    assert r1 == r2

    # Verify no skill_gaps table in PostgreSQL
    result = db_session.execute(
        text("SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='skill_gaps'")
    ).fetchone()
    assert result is None, "Violation: skill_gaps table must NOT exist in the database!"
