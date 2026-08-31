import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.main import app
from backend.app.models.user import User
from backend.app.models.role import Role
from backend.app.models.skill import Skill
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.progress import Progress
from backend.app.services.progress_service import ProgressService

client = TestClient(app)


def test_unauthenticated_progress_rejected():
    """Test that all progress endpoints strictly require authentication."""
    res = client.get("/api/v1/progress")
    assert res.status_code == 401

    res_skills = client.get("/api/v1/progress/skills")
    assert res_skills.status_code == 401

    res_milestones = client.get("/api/v1/progress/milestones")
    assert res_milestones.status_code == 401

    res_next_action = client.get("/api/v1/progress/next-action")
    assert res_next_action.status_code == 401


def test_undocumented_dashboard_endpoint_is_not_public():
    """Verify GET /api/v1/progress/dashboard is not exposed as a public endpoint."""
    res = client.get("/api/v1/progress/dashboard")
    # Should return 404 Not Found (or 405 Method Not Allowed), not a registered public route
    assert res.status_code in [404, 405]


def test_overall_progress_initial_and_after_completion(db_session: Session):
    """Test overall progress calculation from authentic roadmap activity."""
    # 1. Register learner and set target role
    email = f"progress_learner_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "Progress Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    assert reg.status_code == 201
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    assert role is not None

    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)

    # 2. Check initial progress before roadmap generation
    p_init = client.get("/api/v1/progress", headers=headers)
    assert p_init.status_code == 200
    data_init = p_init.json()["data"]
    assert data_init["overall_percentage"] == 0.0
    assert data_init["completed_items"] == 0
    assert data_init["time_spent_minutes"] == 0

    # 3. Generate roadmap
    rm_gen = client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers)
    assert rm_gen.status_code in [200, 201]
    items = rm_gen.json()["data"]["items"]
    assert len(items) > 0
    total_count = len(items)

    # 4. Check progress after roadmap generation
    p_rm = client.get("/api/v1/progress", headers=headers)
    assert p_rm.status_code == 200
    data_rm = p_rm.json()["data"]
    assert data_rm["total_items"] == total_count
    assert data_rm["completed_items"] == 0
    assert data_rm["overall_percentage"] == 0.0
    assert data_rm["time_spent_minutes"] == 0
    assert data_rm["current_milestone"] is not None

    # 5. Start and complete the first available item
    first_item = next((it for it in items if it["status"] == "AVAILABLE"), items[0])
    client.post(f"/api/v1/roadmaps/items/{first_item['id']}/start", headers=headers)
    complete_res = client.post(f"/api/v1/roadmaps/items/{first_item['id']}/complete", headers=headers)
    assert complete_res.status_code == 200

    # 6. Check updated progress
    p_after = client.get("/api/v1/progress", headers=headers)
    assert p_after.status_code == 200
    data_after = p_after.json()["data"]
    assert data_after["completed_items"] == 1
    expected_pct = round((1 / total_count) * 100.0, 2)
    assert data_after["overall_percentage"] == expected_pct
    assert data_after["time_spent_minutes"] == 0  # No artificial time fabricated


def test_real_time_spent_tracking_from_progress_records(db_session: Session):
    """Test that time_spent_minutes is accurately aggregated strictly from actual Progress records."""
    email = f"time_learner_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "Time Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    token = reg.json()["data"]["access_token"]
    user_id = reg.json()["data"]["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)
    rm_gen = client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers)
    items = rm_gen.json()["data"]["items"]

    # Start item 1
    client.post(f"/api/v1/roadmaps/items/{items[0]['id']}/start", headers=headers)

    # Directly verify and add realistic progress elapsed record in DB
    profile = db_session.execute(select(LearnerProfile).where(LearnerProfile.user_id == uuid.UUID(user_id))).scalar_one()
    prog_record = db_session.execute(
        select(Progress).where(Progress.learner_id == profile.id, Progress.roadmap_item_id == uuid.UUID(items[0]["id"]))
    ).scalar_one()
    assert prog_record.started_at is not None

    # Simulate 45 logged study minutes
    prog_record.time_spent_minutes = 45
    db_session.add(prog_record)
    db_session.commit()

    # Query progress endpoint
    p_check = client.get("/api/v1/progress", headers=headers)
    assert p_check.status_code == 200
    assert p_check.json()["data"]["time_spent_minutes"] == 45


def test_progress_formula_consistency_across_endpoints(db_session: Session):
    """Verify that /progress, /roadmaps/current, and /progress/milestones report identical progress math."""
    email = f"formula_learner_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "Formula Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)
    rm_gen = client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers)
    items = rm_gen.json()["data"]["items"]
    total = len(items)

    # Complete first 2 items
    for it in items[:2]:
        client.post(f"/api/v1/roadmaps/items/{it['id']}/start", headers=headers)
        client.post(f"/api/v1/roadmaps/items/{it['id']}/complete", headers=headers)

    expected_overall = round((2 / total) * 100.0, 2)

    # 1. Check /progress
    p_res = client.get("/api/v1/progress", headers=headers)
    assert p_res.json()["data"]["overall_percentage"] == expected_overall
    assert p_res.json()["data"]["completed_items"] == 2

    # 2. Check /roadmaps/current
    rm_res = client.get("/api/v1/roadmaps/current", headers=headers)
    assert rm_res.json()["data"]["overall_progress"] == expected_overall
    assert rm_res.json()["data"]["completed_items"] == 2

    # 3. Check /progress/milestones
    m_res = client.get("/api/v1/progress/milestones", headers=headers)
    milestones = m_res.json()["data"]
    completed_milestones = sum(1 for m in milestones if m["status"] == "COMPLETED")
    assert completed_milestones == 2


def test_skill_progress_tracking(db_session: Session):
    """Test skill-level progress tracking towards target role."""
    email = f"skill_prog_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "Skill Progress Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    assert role is not None
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)

    # Add proficiency for Python
    python_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one_or_none()
    assert python_skill is not None
    client.post("/api/v1/profile/skills", json={
        "skill_id": str(python_skill.id),
        "proficiency": 75.0
    }, headers=headers)

    res = client.get("/api/v1/progress/skills", headers=headers)
    assert res.status_code == 200
    skills_data = res.json()["data"]
    assert len(skills_data) > 0

    py_prog = next((s for s in skills_data if s["skill"] == "Python"), None)
    assert py_prog is not None
    assert py_prog["current_proficiency"] == 75.0
    assert py_prog["required_proficiency"] >= 70.0


def test_milestone_progress_breakdown(db_session: Session):
    """Test milestone-by-milestone status and percentage breakdown."""
    email = f"milestone_prog_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "Milestone Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)
    rm_res = client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers)
    assert rm_res.status_code in [200, 201]

    res = client.get("/api/v1/progress/milestones", headers=headers)
    assert res.status_code == 200
    milestones = res.json()["data"]
    assert len(milestones) > 0

    first_m = milestones[0]
    assert first_m["sequence_order"] == 1
    assert first_m["status"] in ["AVAILABLE", "IN_PROGRESS", "COMPLETED"]
    assert "skill_name" in first_m
    assert "estimated_minutes" in first_m


def test_next_best_action_delegation_to_adaptive_engine(db_session: Session):
    """Test GET /api/v1/progress/next-action delegates strictly to AdaptiveLearningService."""
    email = f"nba_learner_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "NBA Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)
    client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers)

    res = client.get("/api/v1/progress/next-action", headers=headers)
    assert res.status_code == 200
    action = res.json()["data"]
    assert action is not None
    assert "action_type" in action
    assert "title" in action
    assert "reason" in action


def test_internal_dashboard_aggregation_service(db_session: Session):
    """Test internal ProgressService.get_dashboard_data helper correctly computes dynamic metrics."""
    email = f"dash_learner_{uuid.uuid4().hex[:6]}@example.com"
    reg = client.post("/api/v1/auth/register", json={
        "name": "Dashboard Learner",
        "email": email,
        "password": "SecurePassword123!"
    })
    token = reg.json()["data"]["access_token"]
    user_id = reg.json()["data"]["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers)
    client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers)

    d = ProgressService.get_dashboard_data(db=db_session, user_id=uuid.UUID(user_id))

    # 1. Where am I?
    assert d.overview.target_role_title == "AI/ML Engineer"
    assert d.overview.readiness_score >= 0.0
    assert d.overview.overall_progress_percentage == 0.0

    # 2. What have I completed?
    assert d.completed_metrics.completed_milestones_count == 0
    assert d.completed_metrics.mastered_skills_count == 0
    assert d.completed_metrics.total_skills_count > 0

    # 3. What am I weak at?
    assert isinstance(d.weak_areas.weak_skills, list)

    # 4. What am I learning?
    assert d.learning_focus.current_milestone is not None

    # 5. What should I do next?
    assert d.next_best_action is not None
    assert d.next_best_action.action_type in ["study_item", "attempt_assessment", "reinforce_skill", "foundational_intervention"]


def test_user_isolation_on_progress(db_session: Session):
    """Test strict learner isolation across progress endpoints."""
    # User A
    email_a = f"prog_a_{uuid.uuid4().hex[:6]}@example.com"
    reg_a = client.post("/api/v1/auth/register", json={
        "name": "User Progress A",
        "email": email_a,
        "password": "SecurePassword123!"
    })
    token_a = reg_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    email_b = f"prog_b_{uuid.uuid4().hex[:6]}@example.com"
    reg_b = client.post("/api/v1/auth/register", json={
        "name": "User Progress B",
        "email": email_b,
        "password": "SecurePassword123!"
    })
    token_b = reg_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one_or_none()
    client.put("/api/v1/profile", json={"target_role_id": str(role.id)}, headers=headers_a)
    rm_res = client.post("/api/v1/roadmaps/generate", json={"target_role_id": str(role.id)}, headers=headers_a)
    assert rm_res.status_code in [200, 201]

    # User A has roadmap and progress
    res_a = client.get("/api/v1/progress", headers=headers_a)
    assert res_a.json()["data"]["total_items"] > 0

    # User B has no roadmap generated yet
    res_b = client.get("/api/v1/progress", headers=headers_b)
    assert res_b.json()["data"]["total_items"] == 0
    assert res_b.json()["data"]["active_roadmap_id"] is None
