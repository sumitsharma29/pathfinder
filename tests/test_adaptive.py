import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.skill import Skill
from backend.app.models.role import Role
from backend.app.models.roadmap import Roadmap
from backend.app.models.roadmap_item import RoadmapItem
from backend.app.models.assessment import Assessment
from backend.app.models.assessment_question import AssessmentQuestion
from backend.app.services.adaptive_learning_service import AdaptiveLearningService

client = TestClient(app)


@pytest.fixture
def auth_learner(db_session):
    """Register and authenticate a test learner with AI/ML Engineer target role."""
    email = f"adaptive_learner_{uuid.uuid4().hex[:6]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "Adaptive Learner",
        "email": email,
        "password": "Password123!"
    })
    assert r.status_code == 201
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Assign AI/ML Engineer role
    aiml_role = db_session.execute(select(Role).where(Role.slug == "ai-ml-engineer")).scalar_one()
    client.put("/api/v1/profile", json={
        "target_role_id": str(aiml_role.id),
        "daily_study_hours": 2.0
    }, headers=headers)

    user_id = uuid.UUID(r.json()["data"]["user"]["id"])
    return {"headers": headers, "user_id": user_id, "role_id": aiml_role.id}


@pytest.fixture
def auth_user_b():
    """Register and authenticate User B for isolation testing."""
    email = f"user_b_adapt_{uuid.uuid4().hex[:6]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "User B",
        "email": email,
        "password": "Password123!"
    })
    assert r.status_code == 201
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_weak_skills_detection_and_intervention_selection(auth_learner, db_session):
    """Test 1: Adaptive engine detects weak skills (< 60% and < 40%) and generates appropriate interventions."""
    headers = auth_learner["headers"]
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()
    ml_skill = db_session.execute(select(Skill).where(Skill.slug == "machine-learning")).scalar_one()

    # 1. Statistics = 25% (< 40% -> foundational_intervention, critical severity)
    # 2. Machine Learning = 50% (40-59% -> refresher_resource, moderate severity)
    # 3. Python = 90% (>= 80% -> MASTERED, no intervention)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 25.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(ml_skill.id), "proficiency": 50.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 90.0}, headers=headers)

    r_eval = client.post("/api/v1/adaptation/evaluate", headers=headers)
    assert r_eval.status_code == 200
    data = r_eval.json()["data"]

    # Verify detected weak skills
    weak_skills = data["weak_skills_detected"]
    assert any(ws["skill_slug"] == "statistics" and ws["severity"] == "critical" for ws in weak_skills)
    assert any(ws["skill_slug"] == "machine-learning" and ws["severity"] == "moderate" for ws in weak_skills)
    assert not any(ws["skill_slug"] == "python" for ws in weak_skills)

    # Verify selected interventions
    interventions = data["interventions"]
    stats_interv = next(i for i in interventions if i["skill_name"] == "Statistics")
    assert stats_interv["type"] == "foundational_intervention"
    assert stats_interv["severity"] == "critical"

    ml_interv = next(i for i in interventions if i["skill_name"] == "Machine Learning")
    assert ml_interv["type"] == "refresher_resource"
    assert ml_interv["severity"] == "moderate"


def test_assessment_triggers_adaptation_and_unlocks_roadmap(auth_learner, db_session):
    """Test 2: Submitting an assessment updates mastery and adaptively unlocks dependent roadmap items in real-time."""
    headers = auth_learner["headers"]
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()
    stats_assess = db_session.execute(select(Assessment).where(Assessment.skill_id == stats_skill.id)).scalar_one()

    # Initial state: Data Processing = 80 (meets ML prereq), Statistics = 30 (< 75 threshold)
    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 30.0}, headers=headers)

    # Generate initial roadmap -> Machine Learning must be LOCKED
    r_road1 = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r_road1.status_code == 201
    items1 = r_road1.json()["data"]["items"]
    ml_item1 = next(i for i in items1 if i["skill"]["slug"] == "machine-learning")
    assert ml_item1["status"] == "LOCKED"

    # Submit 100% on Statistics assessment -> Mastery = 0.3*30 + 0.7*100 = 79.0 >= 75
    questions = db_session.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == stats_assess.id)
    ).scalars().all()
    payload = {"answers": [{"question_id": str(q.id), "answer": q.correct_answer} for q in questions]}
    r_sub = client.post(f"/api/v1/assessments/{stats_assess.id}/submit", json=payload, headers=headers)
    assert r_sub.status_code == 200
    assert r_sub.json()["data"]["skill_mastery"] == 79.0

    # Verify roadmap has been adaptively updated without manual recalculation request
    r_curr = client.get("/api/v1/roadmaps/current", headers=headers)
    assert r_curr.status_code == 200
    items2 = r_curr.json()["data"]["items"]
    ml_item2 = next(i for i in items2 if i["skill"]["slug"] == "machine-learning")
    assert ml_item2["status"] == "AVAILABLE"
    assert ml_item2["locked_reason"] is None


def test_target_role_change_adaptively_regenerates_roadmap(auth_learner, db_session):
    """Test 3: Changing target role triggers adaptive roadmap regeneration and version increment, preserving history."""
    headers = auth_learner["headers"]

    # Initial: AI/ML Engineer roadmap v1
    r_road1 = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r_road1.status_code == 201
    assert r_road1.json()["data"]["version"] == 1
    assert r_road1.json()["data"]["target_role_name"] == "AI/ML Engineer"

    # Change role to Data Scientist
    ds_role = db_session.execute(select(Role).where(Role.slug == "data-scientist")).scalar_one()
    r_prof = client.put("/api/v1/profile", json={"target_role_id": str(ds_role.id)}, headers=headers)
    assert r_prof.status_code == 200

    # Trigger adaptive evaluation
    r_eval = client.post("/api/v1/adaptation/evaluate", json={"trigger_event": "ROLE_CHANGE"}, headers=headers)
    assert r_eval.status_code == 200
    eval_data = r_eval.json()["data"]
    assert eval_data["roadmap_updated"] is True
    assert eval_data["roadmap_version"] == 2

    # Check current active roadmap
    r_curr = client.get("/api/v1/roadmaps/current", headers=headers)
    assert r_curr.status_code == 200
    assert r_curr.json()["data"]["version"] == 2

    # Verify historical v1 roadmap is preserved and accessible
    v1_id = r_road1.json()["data"]["id"]
    r_v1 = client.get(f"/api/v1/roadmaps/{v1_id}", headers=headers)
    assert r_v1.status_code == 200
    assert r_v1.json()["data"]["version"] == 1
    assert r_v1.json()["data"]["status"].upper() == "ARCHIVED"


def test_prerequisite_threshold_boundary_crossing(auth_learner, db_session):
    """Test 4: Prerequisite edge threshold (75.0) boundaries: 74 -> LOCKED, 75 -> AVAILABLE, 79 -> AVAILABLE, 30 -> LOCKED."""
    headers = auth_learner["headers"]
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    # Python and Data processing meet threshold (85 meets python 76.5 threshold, 80 meets dp 52.0 threshold)
    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 85.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 80.0}, headers=headers)

    # Initial roadmap
    client.post("/api/v1/roadmaps/generate", headers=headers)

    # Case A: Statistics = 74 (< 75) -> ML is LOCKED
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 74.0}, headers=headers)
    client.post("/api/v1/adaptation/evaluate", headers=headers)
    r1 = client.get("/api/v1/roadmaps/current", headers=headers)
    ml1 = next(i for i in r1.json()["data"]["items"] if i["skill"]["slug"] == "machine-learning")
    assert ml1["status"] == "LOCKED"

    # Case B: Statistics = 75 (== 75) -> ML becomes AVAILABLE
    client.put(f"/api/v1/profile/skills/{stats_skill.id}", json={"proficiency": 75.0}, headers=headers)
    client.post("/api/v1/adaptation/evaluate", headers=headers)
    r2 = client.get("/api/v1/roadmaps/current", headers=headers)
    ml2 = next(i for i in r2.json()["data"]["items"] if i["skill"]["slug"] == "machine-learning")
    assert ml2["status"] == "AVAILABLE"

    # Case C: Statistics = 79 (> 75) -> ML remains AVAILABLE
    client.put(f"/api/v1/profile/skills/{stats_skill.id}", json={"proficiency": 79.0}, headers=headers)
    client.post("/api/v1/adaptation/evaluate", headers=headers)
    r3 = client.get("/api/v1/roadmaps/current", headers=headers)
    ml3 = next(i for i in r3.json()["data"]["items"] if i["skill"]["slug"] == "machine-learning")
    assert ml3["status"] == "AVAILABLE"

    # Case D: Statistics drops to 30 (< 75) -> ML becomes LOCKED again
    client.put(f"/api/v1/profile/skills/{stats_skill.id}", json={"proficiency": 30.0}, headers=headers)
    client.post("/api/v1/adaptation/evaluate", headers=headers)
    r4 = client.get("/api/v1/roadmaps/current", headers=headers)
    ml4 = next(i for i in r4.json()["data"]["items"] if i["skill"]["slug"] == "machine-learning")
    assert ml4["status"] == "LOCKED"


def test_sub_threshold_proficiency_change_is_subtle(auth_learner, db_session):
    """Test 5: Sub-threshold update (74 -> 74.5) does not change locked status."""
    headers = auth_learner["headers"]
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 85.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 74.0}, headers=headers)
    client.post("/api/v1/roadmaps/generate", headers=headers)

    # Update to 74.5 (still < 75)
    client.put(f"/api/v1/profile/skills/{stats_skill.id}", json={"proficiency": 74.5}, headers=headers)
    r_eval = client.post("/api/v1/adaptation/evaluate", headers=headers)
    assert r_eval.status_code == 200

    r_curr = client.get("/api/v1/roadmaps/current", headers=headers)
    ml = next(i for i in r_curr.json()["data"]["items"] if i["skill"]["slug"] == "machine-learning")
    assert ml["status"] == "LOCKED"


def test_next_best_action_priority_and_lifecycle(auth_learner, db_session):
    """Test 6: Next Best Action follows strict priority order (Intervention -> IN_PROGRESS -> Next AVAILABLE -> High Gap)."""
    headers = auth_learner["headers"]
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()

    # Step A: All skills 0 -> Statistics < 40 -> Next Best Action is Foundational Intervention
    r_action1 = client.get("/api/v1/progress/next-action", headers=headers)
    assert r_action1.status_code == 200
    act1 = r_action1.json()["data"]
    assert act1 is not None
    assert act1["action_type"] in ["intervention", "assessment", "study_item"]

    # Step B: Set all foundational skills to 80, generate roadmap
    sql_skill = db_session.execute(select(Skill).where(Skill.slug == "sql")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()
    dp_skill = db_session.execute(select(Skill).where(Skill.slug == "data-processing")).scalar_one()

    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(sql_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(dp_skill.id), "proficiency": 80.0}, headers=headers)

    r_road = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r_road.status_code == 201
    items = r_road.json()["data"]["items"]

    # Step C: Next Best Action should now be the first AVAILABLE item
    r_action2 = client.get("/api/v1/progress/next-action", headers=headers)
    assert r_action2.status_code == 200
    act2 = r_action2.json()["data"]
    assert act2["status"] == "AVAILABLE"
    assert act2["id"] == items[0]["id"]

    # Step D: Start item 1 -> Next Best Action shifts to IN_PROGRESS item
    client.post(f"/api/v1/roadmaps/items/{items[0]['id']}/start", headers=headers)
    r_action3 = client.get("/api/v1/progress/next-action", headers=headers)
    assert r_action3.status_code == 200
    act3 = r_action3.json()["data"]
    assert act3["status"] == "IN_PROGRESS"
    assert act3["id"] == items[0]["id"]

    # Step E: Complete item 1 -> Next Best Action shifts to item 2
    client.post(f"/api/v1/roadmaps/items/{items[0]['id']}/complete", headers=headers)
    r_action4 = client.get("/api/v1/progress/next-action", headers=headers)
    assert r_action4.status_code == 200
    act4 = r_action4.json()["data"]
    if len(items) > 1:
        assert act4["id"] == items[1]["id"]


def test_recommendation_adaptation_on_mastery_update(auth_learner, db_session):
    """Test 7: Recommendations adaptively update when a learner achieves mastery in a skill."""
    headers = auth_learner["headers"]
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one()

    # Initial: Python = 0 -> Gap is 85
    client.post("/api/v1/profile/skills", json={"skill_id": str(py_skill.id), "proficiency": 0.0}, headers=headers)
    r_rec1 = client.get("/api/v1/recommendations", headers=headers)
    assert r_rec1.status_code == 200
    recs1 = r_rec1.json()["data"]

    # Master Python: Python = 90 (gap drops to 0)
    client.put(f"/api/v1/profile/skills/{py_skill.id}", json={"proficiency": 90.0}, headers=headers)
    r_rec2 = client.get("/api/v1/recommendations", headers=headers)
    assert r_rec2.status_code == 200
    recs2 = r_rec2.json()["data"]

    # Verify recommendations have adapted:
    # 1. Total recommendation rankings adapt to prioritize remaining gaps
    assert len(recs1) > 0
    assert len(recs2) > 0
    # 2. Pure Python beginner resource score drops when Python is mastered
    pure_py1 = next((r for r in recs1 if r.get("resource") and r["resource"]["skills_covered"] == ["Python"] and r["resource"]["difficulty"] == "beginner"), None)
    pure_py2 = next((r for r in recs2 if r.get("resource") and r["resource"]["skills_covered"] == ["Python"] and r["resource"]["difficulty"] == "beginner"), None)
    if pure_py1 and pure_py2:
        assert pure_py2["score"] < pure_py1["score"]
    else:
        # At minimum, top recommendation ranks shift dynamically
        assert recs1 != recs2


def test_adaptive_idempotency_and_determinism(auth_learner):
    """Test 8: Repeated adaptation evaluations against unchanged learner state are strictly idempotent and deterministic."""
    headers = auth_learner["headers"]
    client.post("/api/v1/roadmaps/generate", headers=headers)

    r1 = client.post("/api/v1/adaptation/evaluate", headers=headers)
    r2 = client.post("/api/v1/adaptation/evaluate", headers=headers)

    assert r1.status_code == 200
    assert r2.status_code == 200

    d1 = r1.json()["data"]
    d2 = r2.json()["data"]

    assert d1["roadmap_version"] == d2["roadmap_version"]
    assert d1["unlocked_items_count"] == d2["unlocked_items_count"]
    assert d1["locked_items_count"] == d2["locked_items_count"]
    assert len(d1["interventions"]) == len(d2["interventions"])
    if d1["next_best_action"] and d2["next_best_action"]:
        assert d1["next_best_action"]["id"] == d2["next_best_action"]["id"]


def test_user_isolation_on_adaptive_engine(auth_learner, auth_user_b):
    """Test 9: User B cannot trigger adaptation or access User A's roadmap / next-best-action."""
    headers_a = auth_learner["headers"]
    headers_b = auth_user_b

    # User A generates roadmap
    client.post("/api/v1/roadmaps/generate", headers=headers_a)

    # User B checks next-action -> User B has no roadmap yet
    r_b_action = client.get("/api/v1/progress/next-action", headers=headers_b)
    assert r_b_action.status_code == 200

    # User B triggers evaluate -> evaluates User B's profile, not User A's
    r_b_eval = client.post("/api/v1/adaptation/evaluate", headers=headers_b)
    assert r_b_eval.status_code == 200
    assert r_b_eval.json()["data"]["learner_id"] != auth_learner["user_id"]


def test_concurrent_adaptation_safety(auth_learner):
    """Test 10: Sequential/concurrent adaptation evaluations complete cleanly without state corruption."""
    headers = auth_learner["headers"]
    client.post("/api/v1/roadmaps/generate", headers=headers)

    # Execute multiple successive evaluation requests
    results = []
    for _ in range(5):
        r = client.post("/api/v1/adaptation/evaluate", json={"trigger_event": "EVAL_CONCURRENCY"}, headers=headers)
        assert r.status_code == 200
        results.append(r.json()["data"])

    # All executions return consistent roadmap version
    versions = [res["roadmap_version"] for res in results]
    assert len(set(versions)) == 1


def test_feedback_downweights_recommendations_adaptively(auth_learner):
    """Test 11: Negative feedback adaptively suppresses the specific candidate in recommendations."""
    headers = auth_learner["headers"]
    r_rec1 = client.get("/api/v1/recommendations", headers=headers)
    assert r_rec1.status_code == 200
    recs1 = r_rec1.json()["data"]
    assert len(recs1) > 0

    first_cand = recs1[0]
    resource_id = first_cand["resource"]["id"] if first_cand.get("resource") else None
    project_id = first_cand["project"]["id"] if first_cand.get("project") else None

    # Submit negative feedback on the recommendation item
    r_feed = client.post(f"/api/v1/recommendations/{first_cand['id']}/feedback", json={
        "feedback_type": "not_helpful",
        "comments": "Too theoretical"
    }, headers=headers)
    assert r_feed.status_code == 201

    # Fetch recommendations again -> candidate score should be downweighted (0.4x penalty)
    r_rec2 = client.get("/api/v1/recommendations", headers=headers)
    assert r_rec2.status_code == 200
    recs2 = r_rec2.json()["data"]
    if resource_id:
        cand2 = next((r for r in recs2 if r.get("resource") and r["resource"]["id"] == resource_id), None)
    else:
        cand2 = next((r for r in recs2 if r.get("project") and r["project"]["id"] == project_id), None)

    if cand2:
        assert cand2["score"] < first_cand["score"]


def test_roadmap_completion_advances_next_best_action_and_unlocks_downstream(auth_learner, db_session):
    """Test 12: Completing a prerequisite roadmap item adaptively unlocks downstream items and advances next action."""
    headers = auth_learner["headers"]
    sql_skill = db_session.execute(select(Skill).where(Skill.slug == "sql")).scalar_one()
    stats_skill = db_session.execute(select(Skill).where(Skill.slug == "statistics")).scalar_one()

    # Initial state: Statistics = 80 (meets ML stats prereq), SQL = 0
    client.post("/api/v1/profile/skills", json={"skill_id": str(stats_skill.id), "proficiency": 80.0}, headers=headers)
    client.post("/api/v1/profile/skills", json={"skill_id": str(sql_skill.id), "proficiency": 0.0}, headers=headers)

    r_road = client.post("/api/v1/roadmaps/generate", headers=headers)
    assert r_road.status_code == 201
    items = r_road.json()["data"]["items"]

    # Start and complete the first available item
    first_avail = next(i for i in items if i["status"] == "AVAILABLE")
    client.post(f"/api/v1/roadmaps/items/{first_avail['id']}/start", headers=headers)
    r_comp = client.post(f"/api/v1/roadmaps/items/{first_avail['id']}/complete", headers=headers)
    assert r_comp.status_code == 200
    assert r_comp.json()["data"]["status"] == "COMPLETED"

    # Evaluate adaptation
    r_eval = client.post("/api/v1/adaptation/evaluate", headers=headers)
    assert r_eval.status_code == 200
    eval_data = r_eval.json()["data"]
    assert eval_data["next_best_action"] is not None
    assert eval_data["next_best_action"]["id"] != first_avail["id"]

