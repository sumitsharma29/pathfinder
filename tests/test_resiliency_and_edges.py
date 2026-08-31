import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def register_clean_user():
    """Helper to register a clean user without roadmap or skills."""
    email = f"empty_{uuid.uuid4().hex[:8]}@example.com"
    res = client.post("/api/v1/auth/register", json={
        "name": "Empty State User",
        "email": email,
        "password": "Password123!"
    })
    assert res.status_code == 201
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_empty_state_resiliency_for_new_learner():
    """Test 1: Brand-new learner receives clean empty state responses without crashing (TESTING_SPEC.md §56)."""
    headers = register_clean_user()

    # Progress on fresh learner
    prog_res = client.get("/api/v1/progress", headers=headers)
    assert prog_res.status_code == 200
    p_data = prog_res.json()["data"]
    assert p_data["overall_percentage"] == 0.0
    assert p_data["completed_items"] == 0

    # Skills progress on fresh learner
    skills_p = client.get("/api/v1/progress/skills", headers=headers)
    assert skills_p.status_code == 200
    assert isinstance(skills_p.json()["data"], list)

    # Current roadmap when none generated
    rm_res = client.get("/api/v1/roadmaps/current", headers=headers)
    assert rm_res.status_code in [200, 404]

    # Assistant conversations on fresh learner
    convs_res = client.get("/api/v1/assistant/conversations", headers=headers)
    assert convs_res.status_code == 200
    assert convs_res.json()["data"] == []


def test_pagination_boundary_validation():
    """Test 2: Pagination boundaries (page >= 1, page_size within 1..100) are enforced (TESTING_SPEC.md §55)."""
    headers = register_clean_user()

    # Valid pagination
    valid_res = client.get("/api/v1/resources?page=1&page_size=10", headers=headers)
    assert valid_res.status_code == 200
    assert valid_res.json()["data"]["page"] == 1
    assert valid_res.json()["data"]["page_size"] == 10

    # Invalid page=0
    inv_page = client.get("/api/v1/resources?page=0&page_size=10", headers=headers)
    assert inv_page.status_code in [400, 422]

    # Invalid page_size=101
    inv_size = client.get("/api/v1/resources?page=1&page_size=101", headers=headers)
    assert inv_size.status_code in [400, 422]


def test_invalid_uuid_handling():
    """Test 3: Non-existent UUIDs return clean 404s without uncaught exceptions or tracebacks."""
    headers = register_clean_user()
    fake_uuid = str(uuid.uuid4())

    # Invalid resource ID
    res = client.get(f"/api/v1/resources/{fake_uuid}", headers=headers)
    assert res.status_code == 404
    assert res.json()["success"] is False
    assert "error" in res.json()

    # Invalid assessment ID
    asm_res = client.get(f"/api/v1/assessments/{fake_uuid}", headers=headers)
    assert asm_res.status_code == 404
    assert asm_res.json()["success"] is False

    # Invalid roadmap item ID
    item_res = client.get(f"/api/v1/roadmaps/items/{fake_uuid}", headers=headers)
    assert item_res.status_code == 404
    assert item_res.json()["success"] is False
