import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_complete_13_step_learner_lifecycle_journey():
    """Test full authoritative 13-step learner lifecycle journey from Landing to AI Assistant (TESTING_SPEC.md §58)."""
    # -------------------------------------------------------------------------
    # STEP 1 — LANDING & PUBLIC HEALTH PROBES
    # -------------------------------------------------------------------------
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ok"

    roles_res = client.get("/api/v1/roles")
    assert roles_res.status_code == 200
    roles_list = roles_res.json()["data"]
    assert len(roles_list) >= 8

    # -------------------------------------------------------------------------
    # STEP 2 — REGISTRATION & AUTHENTICATION
    # -------------------------------------------------------------------------
    email = f"journey_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "E2E Journey Learner",
        "email": email,
        "password": "SecureJourneyPassword123!"
    })
    assert reg_res.status_code == 201
    auth_data = reg_res.json()["data"]
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == email

    # -------------------------------------------------------------------------
    # STEP 3 — ONBOARDING GOAL ANALYSIS
    # -------------------------------------------------------------------------
    goal_res = client.post("/api/v1/ai/analyze-goal", json={
        "text": "I want to become an AI/ML Engineer in 24 weeks.",
        "goal_text": "I want to become an AI/ML Engineer in 24 weeks."
    }, headers=headers)
    assert goal_res.status_code == 200
    goal_data = goal_res.json()["data"]
    assert goal_data["status"] in ["RESOLVED", "AMBIGUOUS"]

    # -------------------------------------------------------------------------
    # STEP 4 — CONFIRM PROFILE & TARGET ROLE
    # -------------------------------------------------------------------------
    aiml_role = next(r for r in roles_list if r["slug"] == "ai-ml-engineer")
    prof_update = client.put("/api/v1/profile", json={
        "target_role_id": aiml_role["id"],
        "daily_study_hours": 2.0
    }, headers=headers)
    assert prof_update.status_code == 200
    assert prof_update.json()["data"]["target_role"]["id"] == aiml_role["id"]

    # -------------------------------------------------------------------------
    # STEP 5 — DYNAMIC SKILL GAP ANALYSIS
    # -------------------------------------------------------------------------
    gaps_res = client.get("/api/v1/skill-gaps", headers=headers)
    assert gaps_res.status_code == 200
    gaps_data = gaps_res.json()["data"]
    assert gaps_data["target_role_id"] == aiml_role["id"]
    assert len(gaps_data["skills"]) > 0

    # -------------------------------------------------------------------------
    # STEP 6 — ROADMAP GENERATION
    # -------------------------------------------------------------------------
    gen_res = client.post("/api/v1/roadmaps/generate", json={
        "target_role_id": aiml_role["id"],
        "target_duration_weeks": 24
    }, headers=headers)
    assert gen_res.status_code == 201
    roadmap = gen_res.json()["data"]
    assert roadmap["target_role_id"] == aiml_role["id"]
    assert len(roadmap["items"]) > 0

    # -------------------------------------------------------------------------
    # STEP 7 — EXPLAINABLE RECOMMENDATIONS & "WHY THIS?"
    # -------------------------------------------------------------------------
    recs_res = client.get("/api/v1/recommendations", headers=headers)
    assert recs_res.status_code == 200
    recs_data = recs_res.json()["data"]
    assert len(recs_data) > 0
    top_rec = recs_data[0]
    assert "reason" in top_rec
    assert "explanation" in top_rec["reason"]

    # -------------------------------------------------------------------------
    # STEP 8 — LEARNING MILESTONE LIFECYCLE (START & COMPLETE)
    # -------------------------------------------------------------------------
    avail_items = [it for it in roadmap["items"] if it["status"] == "AVAILABLE"]
    assert len(avail_items) > 0
    first_item = avail_items[0]

    # Start item -> IN_PROGRESS
    start_res = client.post(f"/api/v1/roadmaps/items/{first_item['id']}/start", headers=headers)
    assert start_res.status_code == 200
    assert start_res.json()["data"]["status"] == "IN_PROGRESS"

    # Complete item -> COMPLETED
    comp_res = client.post(f"/api/v1/roadmaps/items/{first_item['id']}/complete", headers=headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["data"]["status"] == "COMPLETED"

    # -------------------------------------------------------------------------
    # STEP 9 — ASSESSMENT DELIVERY & SERVER-SIDE GRADING
    # -------------------------------------------------------------------------
    assessments_res = client.get("/api/v1/assessments", headers=headers)
    assert assessments_res.status_code == 200
    assessments = assessments_res.json()["data"]
    assert len(assessments) > 0
    asm = assessments[0]

    asm_detail = client.get(f"/api/v1/assessments/{asm['id']}", headers=headers).json()["data"]
    questions = asm_detail["questions"]
    assert len(questions) > 0

    # Submit quiz answers
    answers = [{"question_id": q["id"], "answer": "A"} for q in questions]
    sub_res = client.post(f"/api/v1/assessments/{asm['id']}/submit", json={"answers": answers}, headers=headers)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()["data"]
    assert "score" in sub_data
    assert "passed" in sub_data

    # -------------------------------------------------------------------------
    # STEP 10 & 11 — ADAPTIVE UPDATE & INTERVENTIONS
    # -------------------------------------------------------------------------
    eval_res = client.post("/api/v1/adaptation/evaluate", headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()["data"]
    assert "evaluated_at" in eval_data
    assert "state_changed" in eval_data

    # -------------------------------------------------------------------------
    # STEP 12 — DASHBOARD & NEXT BEST ACTION
    # -------------------------------------------------------------------------
    prog_res = client.get("/api/v1/progress", headers=headers)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()["data"]
    assert prog_data["completed_items"] >= 1
    assert prog_data["overall_percentage"] > 0.0

    nba_res = client.get("/api/v1/progress/next-action", headers=headers)
    assert nba_res.status_code == 200
    assert "action_type" in nba_res.json()["data"]

    # -------------------------------------------------------------------------
    # STEP 13 — GROUNDED AI ASSISTANT WITH CITATIONS
    # -------------------------------------------------------------------------
    chat_res = client.post("/api/v1/assistant/chat", json={
        "message": "What should I study next for machine learning?"
    }, headers=headers)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()["data"]
    assert "message" in chat_data
    assert "conversation_id" in chat_data
    assert isinstance(chat_data["sources"], list)
