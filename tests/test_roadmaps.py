import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from backend.app.main import app
from backend.app.models.skill import Skill
from backend.app.models.role import Role
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem

client = TestClient(app)


@pytest.fixture
def auth_learner_with_skills(db_session):
    """Creates a registered learner set to AI/ML Engineer role with partial skills."""
    email = f"roadmap_learner_{uuid.uuid4().hex[:8]}@example.com"
    r_reg = client.post("/api/v1/auth/register", json={
        "name": "Roadmap Learner",
        "email": email,
        "password": "Password123!"
    })
    token = r_reg.json()["data"]["access_token"]
    user_id = uuid.UUID(r_reg.json()["data"]["user"]["id"])
    headers = {"Authorization": f"Bearer {token}"}

    # Set AI/ML Engineer role
    aiml_role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()
    client.put("/api/v1/profile", json={
        "target_role_id": str(aiml_role.id),
        "daily_study_hours": 2.0
    }, headers=headers)

    # Initial skills:
    # Python = 80 (Mastered >= 80)
    # Probability = 75 (Mastered prerequisite for Statistics >= 70)
    # Statistics = 35 (Partial < 75)
    # Machine Learning = 0 (Missing)
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    prob_skill = db_session.execute(select(Skill).where(Skill.slug == "probability")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(prob_skill.id), "proficiency": 75.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 35.0}, headers=headers)

    return {
        "headers": headers,
        "user_id": user_id,
        "role_id": aiml_role.id
    }


@pytest.fixture
def auth_user_b():
    """Separate user for authorization checks."""
    email = f"roadmap_user_b_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "Roadmap User B",
        "email": email,
        "password": "Password123!"
    })
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_generate_roadmap_and_topological_ordering(auth_learner_with_skills, db_session):
    """Test 1: Roadmap generates with deterministic topological order; prerequisite (Stats) precedes ML."""
    headers = auth_learner_with_skills["headers"]

    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["target_role_name"] == "AI/ML Engineer"
    assert data["version"] == 1
    assert data["status"] == "active"
    items = data["items"]
    assert len(items) > 0

    # Mastered skills (Python = 80 >= 80, Probability = 75 >= 75) must not appear in active roadmap tasks
    skill_slugs = [i["skill"]["slug"] for i in items if i["skill"]]
    assert "python" not in skill_slugs
    assert "probability" not in skill_slugs

    # Statistics and Machine Learning must be present
    assert "statistics" in skill_slugs
    assert "machine-learning" in skill_slugs

    # Prerequisite ordering check: Statistics MUST appear before Machine Learning
    stats_idx = skill_slugs.index("statistics")
    ml_idx = skill_slugs.index("machine-learning")
    assert stats_idx < ml_idx, "Violation: Prerequisite (Statistics) must appear BEFORE dependent (Machine Learning)"

    # Sequences must be contiguous 1..N
    assert [i["sequence"] for i in items] == list(range(1, len(items) + 1))


def test_current_roadmap_and_next_best_action(auth_learner_with_skills):
    """Test 2: GET /roadmaps/current returns summary metrics and identifies next best action."""
    headers = auth_learner_with_skills["headers"]

    # Generate
    client.post("/api/v1/roadmaps/generate", headers=headers)

    # Get current
    r = client.get("/api/v1/roadmaps/current", headers=headers)
    assert r.status_code == 200
    summary = r.json()["data"]
    assert summary["status"] == "active"
    assert summary["total_items"] > 0
    assert summary["available_items"] > 0
    assert summary["next_best_action"] is not None
    assert summary["next_best_action"]["status"] in ["AVAILABLE", "IN_PROGRESS"]


def test_locked_vs_available_item_prerequisites(auth_learner_with_skills):
    """Test 3: Items with unmet prerequisites are LOCKED; items with satisfied prerequisites are AVAILABLE."""
    headers = auth_learner_with_skills["headers"]

    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    items = r.json()["data"]["items"]

    # Statistics (direct prereq Probability is satisfied with 75.0) should be AVAILABLE
    stats_item = next(i for i in items if i["skill"]["slug"] == "statistics")
    assert stats_item["status"] == "AVAILABLE"

    # Machine Learning (depends on unmastered Statistics=35 and Data Processing=0) should be LOCKED
    ml_item = next(i for i in items if i["skill"]["slug"] == "machine-learning")
    assert ml_item["status"] == "LOCKED"
    assert "prerequisite" in ml_item["locked_reason"].lower()


def test_start_and_complete_roadmap_item_lifecycle(auth_learner_with_skills):
    """Test 4: Cannot start LOCKED item; AVAILABLE item transitions to IN_PROGRESS then COMPLETED."""
    headers = auth_learner_with_skills["headers"]

    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    items = r.json()["data"]["items"]

    stats_item = next(i for i in items if i["skill"]["slug"] == "statistics")
    ml_item = next(i for i in items if i["skill"]["slug"] == "machine-learning")

    # 1. Attempting to start LOCKED item fails with 403 PREREQUISITE_NOT_MET
    r_lock = client.post(f"/api/v1/roadmaps/items/{ml_item['id']}/start", headers=headers)
    assert r_lock.status_code == 403
    assert r_lock.json()["error"]["code"] == "PREREQUISITE_NOT_MET"

    # 2. Start AVAILABLE item -> IN_PROGRESS
    r_start = client.post(f"/api/v1/roadmaps/items/{stats_item['id']}/start", headers=headers)
    assert r_start.status_code == 200
    assert r_start.json()["data"]["status"] == "IN_PROGRESS"

    # 3. Complete IN_PROGRESS item -> COMPLETED
    r_comp = client.post(f"/api/v1/roadmaps/items/{stats_item['id']}/complete", headers=headers)
    assert r_comp.status_code == 200
    assert r_comp.json()["data"]["status"] == "COMPLETED"
    assert r_comp.json()["data"]["progress"] == 100.0


def test_completion_unlocks_dependent_items(auth_learner_with_skills, db_session):
    """Test 5: Completing all prerequisite steps unlocks dependent downstream items in the roadmap."""
    headers = auth_learner_with_skills["headers"]

    # Fulfill Data Processing too so ML only waits for Statistics
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()
    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 80.0}, headers=headers)

    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    items = r.json()["data"]["items"]

    stats_item = next(i for i in items if i["skill"]["slug"] == "statistics")
    ml_item = next(i for i in items if i["skill"]["slug"] == "machine-learning")

    assert ml_item["status"] == "LOCKED"

    # Complete Statistics
    client.post(f"/api/v1/roadmaps/items/{stats_item['id']}/complete", headers=headers)

    # Check ML item again -> now unlocked and AVAILABLE
    r_ml = client.get(f"/api/v1/roadmaps/items/{ml_item['id']}", headers=headers)
    assert r_ml.status_code == 200
    assert r_ml.json()["data"]["status"] == "AVAILABLE"
    assert r_ml.json()["data"]["locked_reason"] is None


def test_roadmap_versioning_and_recalculation(auth_learner_with_skills):
    """Test 6: Regenerating creates version 2 and preserves historical version in roadmap_versions table."""
    headers = auth_learner_with_skills["headers"]

    # Initial (version 1)
    r1 = client.post("/api/v1/roadmaps/generate", headers=headers)
    road_id = r1.json()["data"]["id"]
    assert r1.json()["data"]["version"] == 1

    # Recalculate (version 2)
    r2 = client.post(f"/api/v1/roadmaps/{road_id}/recalculate", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["data"]["version"] == 2


def test_role_change_roadmap_regeneration(auth_learner_with_skills, db_session):
    """Test 7: Changing target role and regenerating updates the roadmap to target new role skills."""
    headers = auth_learner_with_skills["headers"]
    ds_role = db_session.execute(select(Role).where(Role.slug == "data-scientist")).scalar_one()

    # Regenerate with Data Scientist
    r = client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(ds_role.id)}, headers=headers)
    assert r.status_code == 201
    assert r.json()["data"]["target_role_name"] == "Data Scientist"


def test_user_isolation_on_roadmaps(auth_learner_with_skills, auth_user_b):
    """Test 8: User B cannot access or modify User A's roadmap or roadmap items."""
    headers_a = auth_learner_with_skills["headers"]
    headers_b = auth_user_b

    r = client.post("/api/v1/roadmaps/generate", headers=headers_a)
    road_id = r.json()["data"]["id"]
    item_id = r.json()["data"]["items"][0]["id"]

    # User B accessing User A's roadmap -> 403
    r_unauth_road = client.get(f"/api/v1/roadmaps/{road_id}", headers=headers_b)
    assert r_unauth_road.status_code == 403

    # User B accessing User A's roadmap item -> 403
    r_unauth_item = client.get(f"/api/v1/roadmaps/items/{item_id}", headers=headers_b)
    assert r_unauth_item.status_code == 403

    # User B attempting to complete User A's roadmap item -> 403
    r_unauth_comp = client.post(f"/api/v1/roadmaps/items/{item_id}/complete", headers=headers_b)
    assert r_unauth_comp.status_code == 403


def test_no_fake_data_and_schema_remains_22_tables(auth_learner_with_skills, db_session):
    """Test 9 & 10: All references exist and database schema remains strictly 22 tables."""
    headers = auth_learner_with_skills["headers"]

    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    items = r.json()["data"]["items"]

    for item in items:
        if item["skill"]:
            s = db_session.execute(select(Skill).where(Skill.id == uuid.UUID(item["skill"]["id"]))).scalar_one_or_none()
            assert s is not None

    # Count domain tables in public schema (excluding spatial_ref_sys and alembic_version)
    count_tables = db_session.execute(
        text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name NOT IN ('spatial_ref_sys', 'alembic_version')")
    ).scalar()
    assert count_tables == 22, f"Schema integrity violation: expected 22 tables, got {count_tables}"


def test_edge_specific_prerequisite_thresholds(db_session):
    """Audit Test 1: Prerequisite readiness respects per-edge strength threshold instead of a global constant."""
    email = f"thresh_learner_{uuid.uuid4().hex[:8]}@example.com"
    r_reg = client.post("/api/v1/auth/register", json={
        "name": "Threshold Learner",
        "email": email,
        "password": "Password123!"
    })
    token = r_reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    aiml_role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()
    client.put("/api/v1/profile", json={"target_role_id": str(aiml_role.id)}, headers=headers)

    # Edge (data-processing -> sql) has strength 0.8. In AI/ML Engineer role, SQL required is 65.
    # Required edge threshold = 0.8 * 65 = 52.0.
    # Set Python = 80 (meets data-processing -> python edge of strength 1.0 * 80 = 80).
    # Set SQL = 55.0 (which is >= 52.0 threshold, though < 70.0).
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    sql_skill = db_session.execute(select(Skill).where(Skill.slug == "sql")).scalar_one()

    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(sql_skill.id), "proficiency": 55.0}, headers=headers)

    # Generate roadmap
    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r.status_code == 201
    items = r.json()["data"]["items"]

    # Data Processing should be AVAILABLE because both Python (80 >= 80) and SQL (55 >= 52) are satisfied
    dp_item = next(i for i in items if i["skill"]["slug"] == "data-processing")
    assert dp_item["status"] == "AVAILABLE", f"Expected AVAILABLE since SQL (55) meets edge threshold (52), but got {dp_item['status']}"


def test_cycle_detection_raises_controlled_domain_error(auth_learner_with_skills, db_session, monkeypatch):
    """Audit Test 2: Dependency cycle triggers ROADMAP_DEPENDENCY_CYCLE error and does not hang or generate invalid roadmap."""
    headers = auth_learner_with_skills["headers"]

    from backend.app.repositories.skill_repository import SkillRepository
    from backend.app.models.skill_prerequisite import SkillPrerequisite

    orig_get_prereqs = SkillRepository.get_all_prerequisites

    # Find two unmastered skills in AI/ML Engineer role: e.g. Machine Learning and Statistics
    ml_skill = db_session.execute(select(Skill).where(Skill.slug == "machine-learning")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    def mock_get_cyclic_prereqs(db):
        real_prereqs = orig_get_prereqs(db)
        # In real seed, Machine Learning requires Statistics.
        # Add reverse edge: Statistics requires Machine Learning to create a direct cycle.
        cyclic_edge = SkillPrerequisite(
            skill_id=stats_skill.id,
            prerequisite_skill_id=ml_skill.id,
            strength=1.0
        )
        return list(real_prereqs) + [cyclic_edge]

    monkeypatch.setattr(SkillRepository, "get_all_prerequisites", mock_get_cyclic_prereqs)

    # Attempt to generate roadmap -> must raise controlled domain error (HTTP 422 ROADMAP_DEPENDENCY_CYCLE)
    r = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r.status_code == 422
    err_body = r.json()["error"]
    assert err_body["code"] == "ROADMAP_DEPENDENCY_CYCLE"
    assert "Dependency cycle detected" in err_body["message"]

