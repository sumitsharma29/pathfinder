import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from backend.app.main import app
from backend.app.models.assessment import Assessment
from backend.app.models.assessment_question import AssessmentQuestion
from backend.app.models.skill import Skill
from backend.app.models.role import Role

client = TestClient(app)


@pytest.fixture
def auth_learner(db_session):
    """Registers a clean test learner."""
    email = f"assess_learner_{uuid.uuid4().hex[:8]}@example.com"
    r_reg = client.post("/api/v1/auth/register", json={
        "name": "Assessment Learner",
        "email": email,
        "password": "Password123!"
    })
    token = r_reg.json()["data"]["access_token"]
    user_id = uuid.UUID(r_reg.json()["data"]["user"]["id"])
    headers = {"Authorization": f"Bearer {token}"}

    # Set AI/ML Engineer role
    aiml_role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()
    client.put("/api/v1/profile", json={"target_role_id": str(aiml_role.id)}, headers=headers)

    return {
        "headers": headers,
        "user_id": user_id,
        "role_id": aiml_role.id
    }


@pytest.fixture
def auth_user_b():
    """Separate user for authorization checks."""
    email = f"assess_user_b_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "Assessment User B",
        "email": email,
        "password": "Password123!"
    })
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_and_get_assessment_catalog(auth_learner, db_session):
    """Test 1: List assessments and retrieve question detail WITHOUT leaking correct answers."""
    headers = auth_learner["headers"]

    # 1. List assessments
    r_list = client.get("/api/v1/assessments", headers=headers)
    assert r_list.status_code == 200
    data = r_list.json()["data"]
    assert len(data) >= 5

    # 2. Get single assessment detail
    py_assess = next(a for a in data if "Python" in a["title"])
    r_detail = client.get(f"/api/v1/assessments/{py_assess['id']}", headers=headers)
    assert r_detail.status_code == 200
    detail = r_detail.json()["data"]
    assert detail["title"] == py_assess["title"]
    assert len(detail["questions"]) == 2

    # CRITICAL SECURITY CHECK: No correct_answer or explanation in question payload
    for q in detail["questions"]:
        assert "correct_answer" not in q
        assert "explanation" not in q
        assert q["question"] is not None
        assert q["points"] > 0


def test_invalid_assessment_id_returns_404(auth_learner):
    """Test 2: Requesting non-existent assessment ID returns 404."""
    headers = auth_learner["headers"]
    fake_id = uuid.uuid4()
    r = client.get(f"/api/v1/assessments/{fake_id}", headers=headers)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_submission_scoring_100_percent(auth_learner, db_session):
    """Test 3: 100% correct answers produces 100.0 score and passed=True."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()

    # Load actual questions
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    submission_payload = {
        "answers": [
            {"question_id": str(q.id), "answer": q.correct_answer}
            for q in questions
        ]
    }

    r = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=submission_payload, headers=headers)
    assert r.status_code == 200
    res = r.json()["data"]
    assert res["score"] == 100.0
    assert res["passed"] is True
    assert res["correct_count"] == len(questions)
    assert res["attempt_number"] == 1


def test_submission_scoring_50_percent(auth_learner, db_session):
    """Test 4: 50% correct answers produces 50.0 score."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    # 1 correct, 1 wrong
    submission_payload = {
        "answers": [
            {"question_id": str(questions[0].id), "answer": questions[0].correct_answer},
            {"question_id": str(questions[1].id), "answer": "WRONG_ANSWER"}
        ]
    }

    r = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=submission_payload, headers=headers)
    assert r.status_code == 200
    res = r.json()["data"]
    assert res["score"] == 50.0
    assert res["correct_count"] == 1
    assert res["passed"] is False  # 50 < passing_score of 70


def test_submission_scoring_0_percent(auth_learner, db_session):
    """Test 5: 0% correct answers produces 0.0 score."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    submission_payload = {
        "answers": [
            {"question_id": str(q.id), "answer": "INCORRECT"}
            for q in questions
        ]
    }

    r = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=submission_payload, headers=headers)
    assert r.status_code == 200
    res = r.json()["data"]
    assert res["score"] == 0.0
    assert res["correct_count"] == 0
    assert res["passed"] is False


def test_submission_validation_errors(auth_learner, db_session):
    """Test 6: Strict validation against unknown IDs, duplicates, cross-assessment IDs, and incomplete submissions."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    stats_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Statistical%"))).scalar_one()

    py_questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()
    stats_questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == stats_assess.id)
    ).scalars().all()

    # 1. Unknown Question ID -> 422 INVALID_QUESTION_ID
    r1 = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json={
        "answers": [
            {"question_id": str(uuid.uuid4()), "answer": "A"},
            {"question_id": str(py_questions[1].id), "answer": "B"}
        ]
    }, headers=headers)
    assert r1.status_code == 422
    assert r1.json()["error"]["code"] == "INVALID_QUESTION_ID"

    # 2. Cross-Assessment Question ID -> 422 INVALID_QUESTION_ID
    r2 = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json={
        "answers": [
            {"question_id": str(stats_questions[0].id), "answer": "A"},
            {"question_id": str(py_questions[1].id), "answer": "B"}
        ]
    }, headers=headers)
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "INVALID_QUESTION_ID"

    # 3. Duplicate Question ID -> 422 DUPLICATE_QUESTION_SUBMISSION
    r3 = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json={
        "answers": [
            {"question_id": str(py_questions[0].id), "answer": "A"},
            {"question_id": str(py_questions[0].id), "answer": "B"}
        ]
    }, headers=headers)
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "DUPLICATE_QUESTION_SUBMISSION"

    # 4. Missing Question (Incomplete submission) -> 422 INCOMPLETE_SUBMISSION
    r4 = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json={
        "answers": [
            {"question_id": str(py_questions[0].id), "answer": "A"}
        ]
    }, headers=headers)
    assert r4.status_code == 422
    assert r4.json()["error"]["code"] == "INCOMPLETE_SUBMISSION"


def test_client_score_manipulation_ignored(auth_learner, db_session):
    """Test 6b: Malicious client-injected score/mastery/passed fields are ignored; server computes real score."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    # Scenario A: Client submits WRONG answers but injects score: 100, passed: true, correct_count: 999, mastery: 100
    malicious_payload = {
        "answers": [
            {"question_id": str(q.id), "answer": "WRONG_ANSWER"}
            for q in questions
        ],
        "score": 100.0,
        "percentage": 100.0,
        "passed": True,
        "correct_count": 999,
        "skill_mastery": 100.0,
        "attempt_number": 99
    }

    r_a = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=malicious_payload, headers=headers)
    assert r_a.status_code == 200
    res_a = r_a.json()["data"]
    # Server calculates 0.0 despite malicious client payload
    assert res_a["score"] == 0.0
    assert res_a["passed"] is False
    assert res_a["correct_count"] == 0
    assert res_a["attempt_number"] == 1  # Server assigned real attempt 1, not 99

    # Scenario B: Client submits CORRECT answers but injects score: 0, passed: false
    malicious_payload_b = {
        "answers": [
            {"question_id": str(q.id), "answer": q.correct_answer}
            for q in questions
        ],
        "score": 0.0,
        "passed": False
    }

    r_b = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=malicious_payload_b, headers=headers)
    assert r_b.status_code == 200
    res_b = r_b.json()["data"]
    # Server calculates 100.0 despite malicious client payload
    assert res_b["score"] == 100.0
    assert res_b["passed"] is True
    assert res_b["correct_count"] == len(questions)
    assert res_b["attempt_number"] == 2


def test_attempt_number_auto_increment_and_history(auth_learner, db_session):
    """Test 7: Attempt numbers increment automatically (1 -> 2) and all attempts are preserved in history."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    payload = {
        "answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]
    }

    # Attempt 1
    r1 = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=payload, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["data"]["attempt_number"] == 1

    # Attempt 2
    r2 = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=payload, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["data"]["attempt_number"] == 2

    # Query history
    r_hist = client.get("/api/v1/assessments/results", headers=headers)
    assert r_hist.status_code == 200
    history = r_hist.json()["data"]
    assert len(history) >= 2
    assert history[0]["attempt_number"] == 2
    assert history[1]["attempt_number"] == 1


def test_mastery_calculation_and_learner_skill_update(auth_learner, db_session):
    """Test 8: Mastery calculates with evidence fusion formula (0.30 * old + 0.70 * score) and updates learner skill."""
    headers = auth_learner["headers"]
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    py_assess = db_session.execute(select(Assessment).where(Assessment.skill_id == py_skill.id)).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    # 1. Set initial Python proficiency = 40.0
    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 40.0}, headers=headers)

    # 2. Score 100% on assessment
    # Expected new mastery = 0.30 * 40.0 + 0.70 * 100.0 = 12.0 + 70.0 = 82.0
    payload = {
        "answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]
    }
    r = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["data"]["skill_mastery"] == 82.0

    # 3. Check learner's profile skills
    r_skills = client.get("/api/v1/profile/skills", headers=headers)
    assert r_skills.status_code == 200
    skills_data = r_skills.json()["data"]
    py_record = next(s for s in skills_data if s["skill_slug"] == "python")
    assert py_record["proficiency"] == 82.0
    assert py_record["source"] == "assessment"


def test_dynamic_skill_gap_immediately_reflects_assessment_mastery(auth_learner, db_session):
    """Test 9: Passing an assessment immediately reduces dynamic skill gap in real time without stale cache."""
    headers = auth_learner["headers"]
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()
    stats_assess = db_session.execute(select(Assessment).where(Assessment.skill_id == stats_skill.id)).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == stats_assess.id)
    ).scalars().all()

    # Initial Statistics = 0 -> Gap is 75 in AI/ML Engineer
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 0.0}, headers=headers)
    r_gap1 = client.get("/api/v1/skill-gaps", headers=headers)
    stats_gap1 = next(s for s in r_gap1.json()["data"]["skills"] if s["skill_slug"] == "statistics")
    assert stats_gap1["gap"] == 75.0

    # Submit 100% on Statistics assessment
    # New mastery = 0.3 * 0 + 0.7 * 100 = 70.0
    payload = {
        "answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]
    }
    client.post(f"/api/v1/assessments/{stats_assess.id}/submit", json=payload, headers=headers)

    # Re-check dynamic skill gaps
    r_gap2 = client.get("/api/v1/skill-gaps", headers=headers)
    stats_gap2 = next(s for s in r_gap2.json()["data"]["skills"] if s["skill_slug"] == "statistics")
    assert stats_gap2["gap"] == 5.0  # 75 - 70 = 5.0 gap remaining
    assert stats_gap2["current"] == 70.0


def test_user_isolation_on_assessments(auth_learner, auth_user_b, db_session):
    """Test 10: User B cannot view User A's assessment results, and User A's submission doesn't affect User B."""
    headers_a = auth_learner["headers"]
    headers_b = auth_user_b

    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    # User A submits
    payload = {
        "answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]
    }
    client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=payload, headers=headers_a)

    # User B checks history -> should be empty
    r_b_hist = client.get("/api/v1/assessments/results", headers=headers_b)
    assert r_b_hist.status_code == 200
    assert len(r_b_hist.json()["data"]) == 0


def test_assessment_mastery_unlocks_roadmap_prerequisite(auth_learner, db_session):
    """Test 11: Achieving mastery via assessment satisfies prerequisite and makes dependent roadmap item AVAILABLE."""
    headers = auth_learner["headers"]

    # Initial state: Data Processing = 80 (meets ML prereq), Statistics = 0 (< 70).
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()
    stats_assess = db_session.execute(select(Assessment).where(Assessment.skill_id == stats_skill.id)).scalar_one()

    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 30.0}, headers=headers)

    # Generate initial roadmap -> Machine Learning should be LOCKED because Statistics (30 < 75) is unmet
    r_road1 = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r_road1.status_code == 201
    items1 = r_road1.json()["data"]["items"]
    ml_item1 = next(i for i in items1 if i["skill"]["slug"] == "machine-learning")
    assert ml_item1["status"] == "LOCKED"

    # Take and score 100% on Statistics assessment
    # Stats new mastery = 0.3 * 30 + 0.7 * 100 = 79.0 (meets edge threshold of 1.0 * 75 = 75)
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == stats_assess.id)
    ).scalars().all()
    payload = {"answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]}
    client.post(f"/api/v1/assessments/{stats_assess.id}/submit", json=payload, headers=headers)

    # Regenerate/recalculate roadmap -> Machine Learning is now AVAILABLE!
    r_road2 = client.post(f"/api/v1/roadmaps/{r_road1.json()['data']['id']}/recalculate", headers=headers)
    assert r_road2.status_code == 200
    items2 = r_road2.json()["data"]["items"]
    ml_item2 = next(i for i in items2 if i["skill"]["slug"] == "machine-learning")
    assert ml_item2["status"] == "AVAILABLE"
    assert ml_item2["locked_reason"] is None


def test_result_history_immutability_and_no_mutation_api(auth_learner, db_session):
    """Test 12: Historical assessment results cannot be modified or deleted via API."""
    headers = auth_learner["headers"]
    py_assess = db_session.execute(select(Assessment).where(Assessment.title.like("%Python%"))).scalar_one()
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == py_assess.id)
    ).scalars().all()

    # Submit
    payload = {"answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]}
    r_sub = client.post(f"/api/v1/assessments/{py_assess.id}/submit", json=payload, headers=headers)
    result_id = r_sub.json()["data"]["id"]

    # Verify no PUT / PATCH / DELETE routes exist on assessments/results
    r_put = client.put(f"/api/v1/assessments/results/{result_id}", json={"score": 99.0}, headers=headers)
    assert r_put.status_code in [404, 405]

    r_delete = client.delete(f"/api/v1/assessments/results/{result_id}", headers=headers)
    assert r_delete.status_code in [404, 405]

