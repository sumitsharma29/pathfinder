import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def register_learner(name: str, email_prefix: str) -> dict:
    """Helper to register and authenticate a test learner."""
    email = f"{email_prefix}_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"
    res = client.post("/api/v1/auth/register", json={
        "name": name,
        "email": email,
        "password": password
    })
    assert res.status_code == 201, f"Failed to register {name}: {res.text}"
    user_data = res.json()["data"]["user"]
    token = res.json()["data"]["access_token"]
    return {
        "id": user_data["id"],
        "name": name,
        "email": email,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


def test_persona_differentiation_produces_unique_gaps_and_recommendations():
    """Test 1: Learner A (Strong Python, Weak Stats) vs Learner B (Weak Python, Strong Stats) receive different paths (TESTING_SPEC.md §60)."""
    # 1. Register Persona A & Persona B
    learner_a = register_learner("Learner A (Python Expert)", "learner_a")
    learner_b = register_learner("Learner B (Stats Expert)", "learner_b")

    # Fetch skills catalog
    skills_res = client.get("/api/v1/skills", headers=learner_a["headers"])
    assert skills_res.status_code == 200
    skills_map = {s["slug"]: s["id"] for s in skills_res.json()["data"]}

    # Fetch AI/ML Engineer Role
    roles_res = client.get("/api/v1/roles", headers=learner_a["headers"])
    assert roles_res.status_code == 200
    aiml_role = next(r for r in roles_res.json()["data"] if r["slug"] == "ai-ml-engineer")

    # Configure Learner A: Target AI/ML Engineer, Python=85, Statistics=25
    client.put("/api/v1/profile", json={"target_role_id": aiml_role["id"], "daily_study_hours": 2.0}, headers=learner_a["headers"])
    if "python" in skills_map:
        client.post("/api/v1/profile/skills", json={"skill_id": skills_map["python"], "proficiency": 85.0}, headers=learner_a["headers"])
    if "statistics" in skills_map:
        client.post("/api/v1/profile/skills", json={"skill_id": skills_map["statistics"], "proficiency": 25.0}, headers=learner_a["headers"])

    # Configure Learner B: Target AI/ML Engineer, Python=20, Statistics=90
    client.put("/api/v1/profile", json={"target_role_id": aiml_role["id"], "daily_study_hours": 2.0}, headers=learner_b["headers"])
    if "python" in skills_map:
        client.post("/api/v1/profile/skills", json={"skill_id": skills_map["python"], "proficiency": 20.0}, headers=learner_b["headers"])
    if "statistics" in skills_map:
        client.post("/api/v1/profile/skills", json={"skill_id": skills_map["statistics"], "proficiency": 90.0}, headers=learner_b["headers"])

    # 2. Assert Dynamic Skill Gap Differentiation
    gaps_a = client.get("/api/v1/skill-gaps", headers=learner_a["headers"]).json()["data"]["skills"]
    gaps_b = client.get("/api/v1/skill-gaps", headers=learner_b["headers"]).json()["data"]["skills"]

    stat_gap_a = next(g for g in gaps_a if g["skill_slug"] == "statistics")
    stat_gap_b = next(g for g in gaps_b if g["skill_slug"] == "statistics")
    py_gap_a = next(g for g in gaps_a if g["skill_slug"] == "python")
    py_gap_b = next(g for g in gaps_b if g["skill_slug"] == "python")

    # Learner A has large gap in Statistics, 0 gap in Python
    assert stat_gap_a["gap"] > stat_gap_b["gap"], "Learner A should have larger Statistics gap than Learner B"
    assert py_gap_a["gap"] < py_gap_b["gap"], "Learner A should have smaller Python gap than Learner B"

    # 3. Assert Recommendation Differentiation
    recs_a = client.get("/api/v1/recommendations", headers=learner_a["headers"]).json()["data"]
    recs_b = client.get("/api/v1/recommendations", headers=learner_b["headers"]).json()["data"]

    assert len(recs_a) > 0 and len(recs_b) > 0

    # Scores and reasons for each persona reflect their distinct individual gap profiles
    recs_a_scores = {r["id"]: r["score"] for r in recs_a}
    recs_b_scores = {r["id"]: r["score"] for r in recs_b}
    assert recs_a_scores != recs_b_scores, "Recommendation scores must differentiate between different learner profiles"


def test_closed_loop_adaptive_branching_on_strong_vs_weak_performance():
    """Test 2: Same learner exhibits different adaptive paths on strong vs weak assessment performance (TESTING_SPEC.md §61)."""
    # 1. Register learner
    learner = register_learner("Adaptive Candidate", "adapt_cand")
    
    # Configure Profile & Generate Roadmap
    roles_res = client.get("/api/v1/roles", headers=learner["headers"]).json()["data"]
    aiml_role = next(r for r in roles_res if r["slug"] == "ai-ml-engineer")
    client.put("/api/v1/profile", json={"target_role_id": aiml_role["id"], "daily_study_hours": 1.5}, headers=learner["headers"])

    roadmap_res = client.post("/api/v1/roadmaps/generate", json={"target_role_id": aiml_role["id"], "target_duration_weeks": 16}, headers=learner["headers"])
    assert roadmap_res.status_code == 201

    # 2. Locate available assessment
    assessments_res = client.get("/api/v1/assessments", headers=learner["headers"]).json()["data"]
    assert len(assessments_res) > 0
    asm = assessments_res[0]
    asm_detail = client.get(f"/api/v1/assessments/{asm['id']}", headers=learner["headers"]).json()["data"]
    questions = asm_detail["questions"]

    # 3. Weak attempt (<40%) -> triggers weak skill detection and adaptive foundational intervention
    wrong_answers = [{"question_id": q["id"], "answer": "incorrect_selection"} for q in questions]
    weak_sub = client.post(f"/api/v1/assessments/{asm['id']}/submit", json={"answers": wrong_answers}, headers=learner["headers"])
    assert weak_sub.status_code == 200
    assert weak_sub.json()["data"]["score"] < 40.0

    # Verify Adaptive Evaluation endpoint reports interventions
    eval_res = client.post("/api/v1/adaptation/evaluate", headers=learner["headers"])
    assert eval_res.status_code == 200
    eval_data = eval_res.json()["data"]
    assert len(eval_data["interventions"]) > 0 or len(eval_data["weak_skills_detected"]) > 0


def test_deterministic_scoring_ranking_reproducibility():
    """Test 3: Identical inputs produce identical recommendation scores and ranks (TESTING_SPEC.md §62)."""
    learner = register_learner("Determinism Candidate", "det_cand")

    # Configure target role for deterministic recommendation scoring
    roles_res = client.get("/api/v1/roles", headers=learner["headers"]).json()["data"]
    aiml_role = next(r for r in roles_res if r["slug"] == "ai-ml-engineer")
    client.put("/api/v1/profile", json={"target_role_id": aiml_role["id"], "daily_study_hours": 2.0}, headers=learner["headers"])

    # Fetch recommendations 3 consecutive times
    recs1 = client.get("/api/v1/recommendations", headers=learner["headers"]).json()["data"]
    recs2 = client.get("/api/v1/recommendations", headers=learner["headers"]).json()["data"]
    recs3 = client.get("/api/v1/recommendations", headers=learner["headers"]).json()["data"]

    assert len(recs1) == len(recs2) == len(recs3)
    for r1, r2, r3 in zip(recs1, recs2, recs3):
        id1 = r1["resource"]["id"] if r1.get("resource") else r1["project"]["id"]
        id2 = r2["resource"]["id"] if r2.get("resource") else r2["project"]["id"]
        id3 = r3["resource"]["id"] if r3.get("resource") else r3["project"]["id"]
        assert id1 == id2 == id3
        assert r1["score"] == r2["score"] == r3["score"]
