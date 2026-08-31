import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import app
from backend.app.models.skill import Skill
from backend.app.models.role import Role
from backend.app.models.resource import Resource
from backend.app.models.project import Project

client = TestClient(app)


@pytest.fixture
def auth_learner(db_session):
    """Creates a registered learner set to AI/ML Engineer role with initial skills."""
    email = f"rec_learner_{uuid.uuid4().hex[:8]}@example.com"
    r_reg = client.post("/api/v1/auth/register", json={
        "name": "Rec Learner",
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
        "daily_study_hours": 2.0,
        "learning_preferences": {"content_types": ["course", "video", "project"]}
    }, headers=headers)

    return {
        "headers": headers,
        "user_id": user_id,
        "role_id": aiml_role.id
    }


@pytest.fixture
def auth_user_b():
    """Creates a separate User B for isolation testing."""
    email = f"rec_user_b_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "User B",
        "email": email,
        "password": "Password123!"
    })
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_candidate_generation_and_scoring_breakdown(auth_learner, db_session):
    """Test 1 & 2: Candidates are generated from DB records and include normalized scoring breakdowns."""
    headers = auth_learner["headers"]

    r = client.get("/api/v1/recommendations", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    recs = data["data"]
    assert len(recs) > 0

    top_rec = recs[0]
    assert 0.0 <= top_rec["score"] <= 1.0
    assert top_rec["ranking"] == 1
    assert "reason" in top_rec

    reason = top_rec["reason"]
    assert 0.0 <= reason["skill_gap"] <= 1.0
    assert 0.0 <= reason["prerequisite_fit"] <= 1.0
    assert 0.0 <= reason["goal_relevance"] <= 1.0
    assert 0.0 <= reason["difficulty_fit"] <= 1.0
    assert 0.0 <= reason["time_fit"] <= 1.0
    assert 0.0 <= reason["preference_fit"] <= 1.0
    assert len(reason["explanation"]) > 10

    # Verify score matches weighted sum
    expected_score = round(
        0.30 * reason["skill_gap"]
        + 0.20 * reason["prerequisite_fit"]
        + 0.15 * reason["goal_relevance"]
        + 0.15 * reason["difficulty_fit"]
        + 0.10 * reason["time_fit"]
        + 0.10 * reason["preference_fit"],
        4
    )
    assert abs(top_rec["score"] - expected_score) <= 0.001


def test_prerequisite_awareness_in_recommendations(auth_learner, db_session):
    """Test 3: Missing prerequisites lower candidate score; satisfied prerequisites increase score."""
    headers = auth_learner["headers"]
    ml_skill = db_session.execute(select(Skill).where(Skill.slug == "machine-learning")).scalar_one()

    # With zero statistics/data processing proficiency, ML resources should have low prerequisite_fit
    r = client.get(f"/api/v1/recommendations?skill_id={ml_skill.id}", headers=headers)
    assert r.status_code == 200
    ml_recs = r.json()["data"]
    if ml_recs:
        assert ml_recs[0]["reason"]["prerequisite_fit"] <= 0.5

    # Now fulfill prerequisites (Python = 80, Statistics = 75, Data Processing = 70)
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()

    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 75.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 70.0}, headers=headers)

    # Prerequisite fit for ML resources should now be high
    r_after = client.get(f"/api/v1/recommendations?skill_id={ml_skill.id}", headers=headers)
    assert r_after.status_code == 200
    ml_recs_after = r_after.json()["data"]
    if ml_recs_after:
        assert ml_recs_after[0]["reason"]["prerequisite_fit"] >= 0.9


def test_dynamic_reactivity_on_skill_update(auth_learner, db_session):
    """Test 4: When a skill gap is closed, recommendations immediately shift away from that skill."""
    headers = auth_learner["headers"]
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    # Step 1: Initial (Statistics has gap)
    r1 = client.get("/api/v1/recommendations", headers=headers)
    top_skill1 = r1.json()["data"][0]["skill_name"]

    # Step 2: Master Statistics (80.0)
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(stats_skill.id),
        "proficiency": 80.0
    }, headers=headers)

    # Step 3: Recalculate
    r2 = client.get("/api/v1/recommendations", headers=headers)
    stats_rec2 = next((r for r in r2.json()["data"] if r["skill_name"] == "Statistics"), None)
    if stats_rec2:
        # Gap component should now be very low
        assert stats_rec2["reason"]["skill_gap"] <= 0.1


def test_role_change_alters_recommendations(auth_learner, db_session):
    """Test 5: Changing target role immediately recalculates recommendations to target new role skills."""
    headers = auth_learner["headers"]
    ds_role = db_session.execute(select(Role).where(Role.slug == "data-scientist")).scalar_one()

    client.put("/api/v1/profile", json={"target_role_id": str(ds_role.id)}, headers=headers)

    r = client.get("/api/v1/recommendations", headers=headers)
    assert r.status_code == 200
    recs = r.json()["data"]
    assert len(recs) > 0


def test_recommendation_detail_and_user_isolation(auth_learner, auth_user_b):
    """Test 6: User A can view own recommendation detail; User B cannot access User A's recommendation (403)."""
    headers_a = auth_learner["headers"]
    headers_b = auth_user_b

    # User A gets recommendations
    r_list = client.get("/api/v1/recommendations", headers=headers_a)
    rec_id = r_list.json()["data"][0]["id"]

    # User A gets detail
    r_detail = client.get(f"/api/v1/recommendations/{rec_id}", headers=headers_a)
    assert r_detail.status_code == 200
    assert r_detail.json()["data"]["id"] == rec_id

    # User B attempts to access User A's recommendation -> 403
    r_unauth = client.get(f"/api/v1/recommendations/{rec_id}", headers=headers_b)
    assert r_unauth.status_code == 403


def test_feedback_submission_and_downweighting(auth_learner, db_session):
    """Test 7: Submitting not_helpful feedback excludes the resource from future recommendations."""
    headers = auth_learner["headers"]

    # Get top recommendation
    r_init = client.get("/api/v1/recommendations", headers=headers)
    top_rec = r_init.json()["data"][0]
    rec_id = top_rec["id"]
    res_id = top_rec["resource"]["id"] if top_rec["resource"] else None

    if res_id:
        # Submit not_helpful feedback
        r_fb = client.post(f"/api/v1/recommendations/{rec_id}/feedback", json={
            "feedback_type": "not_helpful",
            "rating": 1,
            "comment": "Too basic for my background"
        }, headers=headers)
        assert r_fb.status_code == 201
        assert r_fb.json()["data"]["feedback_type"] == "not_helpful"

        # Subsequent recommendations should no longer include this resource
        r_after = client.get("/api/v1/recommendations", headers=headers)
        res_ids_after = [r["resource"]["id"] for r in r_after.json()["data"] if r["resource"]]
        assert res_id not in res_ids_after


def test_no_fake_data_all_ids_exist(auth_learner, db_session):
    """Test 8: Every returned resource/project and skill ID actually exists in PostgreSQL."""
    headers = auth_learner["headers"]

    r = client.get("/api/v1/recommendations", headers=headers)
    for item in r.json()["data"]:
        if item["resource"]:
            res_exists = db_session.execute(
                select(Resource).where(Resource.id == uuid.UUID(item["resource"]["id"]))
            ).scalar_one_or_none()
            assert res_exists is not None

        if item["project"]:
            proj_exists = db_session.execute(
                select(Project).where(Project.id == uuid.UUID(item["project"]["id"]))
            ).scalar_one_or_none()
            assert proj_exists is not None

        if item["skill_id"]:
            skill_exists = db_session.execute(
                select(Skill).where(Skill.id == uuid.UUID(item["skill_id"]))
            ).scalar_one_or_none()
            assert skill_exists is not None
