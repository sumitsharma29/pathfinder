import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.main import app
from backend.app.models.resource import Resource
from backend.app.models.skill import Skill
from backend.app.models.resource_skill import ResourceSkill

client = TestClient(app)


def test_list_resources_public_and_pagination():
    """Test public resource catalog listing and pagination."""
    res = client.get("/api/v1/resources?page=1&page_size=5")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 5
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total"] >= 10


def test_resource_filtering_by_skill_difficulty_and_type(db_session: Session):
    """Test resource catalog filtering by covered skill, difficulty, and type."""
    # Find Python skill
    py_skill = db_session.execute(select(Skill).where(Skill.slug == "python")).scalar_one_or_none()
    assert py_skill is not None

    # 1. Filter by skill_id
    res_skill = client.get(f"/api/v1/resources?skill_id={py_skill.id}")
    assert res_skill.status_code == 200
    items_skill = res_skill.json()["data"]["items"]
    assert len(items_skill) > 0
    for it in items_skill:
        covered_ids = [s["id"] for s in it["skills"]]
        assert str(py_skill.id) in covered_ids

    # 2. Filter by difficulty
    res_diff = client.get("/api/v1/resources?difficulty=beginner")
    assert res_diff.status_code == 200
    items_diff = res_diff.json()["data"]["items"]
    for it in items_diff:
        assert it["difficulty"].lower() == "beginner"

    # 3. Filter by resource_type
    res_type = client.get("/api/v1/resources?resource_type=course")
    assert res_type.status_code == 200
    items_type = res_type.json()["data"]["items"]
    for it in items_type:
        assert it["resource_type"].lower() == "course"


def test_resource_search_by_query():
    """Test searching resources by title and description keywords."""
    res = client.get("/api/v1/resources?search=Python")
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    assert len(items) > 0
    assert any("python" in it["title"].lower() or "python" in (it["description"] or "").lower() for it in items)


def test_resource_detail_and_skills_mapping(db_session: Session):
    """Test retrieving detailed resource view with associated skills."""
    res_list = client.get("/api/v1/resources?page_size=1")
    first_res = res_list.json()["data"]["items"][0]
    res_id = first_res["id"]

    res_detail = client.get(f"/api/v1/resources/{res_id}")
    assert res_detail.status_code == 200
    d = res_detail.json()["data"]
    assert d["id"] == res_id
    assert d["title"] == first_res["title"]
    assert "skills" in d
    assert isinstance(d["skills"], list)


def test_inactive_resource_excluded_from_catalog(db_session: Session):
    """Test that deactivated resources are excluded from both list and detail endpoints."""
    # Create inactive resource
    inactive = Resource(
        title="Secret Inactive Resource",
        description="Should never appear in catalog",
        resource_type="course",
        url="https://example.com/inactive",
        difficulty="advanced",
        quality_score=99.0,
        estimated_minutes=120,
        is_active=False
    )
    db_session.add(inactive)
    db_session.commit()
    db_session.refresh(inactive)

    # 1. Verify not in list
    res_list = client.get("/api/v1/resources?search=Secret Inactive")
    assert res_list.status_code == 200
    assert len(res_list.json()["data"]["items"]) == 0

    # 2. Verify 404 in detail
    res_detail = client.get(f"/api/v1/resources/{inactive.id}")
    assert res_detail.status_code == 404


def test_internal_embedding_never_exposed(db_session: Session):
    """Test that internal vector embeddings are strictly sanitized and never leaked to API responses."""
    res = client.get("/api/v1/resources?page_size=5")
    assert res.status_code == 200
    for it in res.json()["data"]["items"]:
        assert "embedding" not in it
        assert "vector" not in it

    # Check detail endpoint as well
    first_id = res.json()["data"]["items"][0]["id"]
    res_detail = client.get(f"/api/v1/resources/{first_id}")
    assert res_detail.status_code == 200
    assert "embedding" not in res_detail.json()["data"]
    assert "vector" not in res_detail.json()["data"]


def test_invalid_resource_id_returns_404():
    """Test that querying a non-existent resource ID returns HTTP 404."""
    fake_id = uuid.uuid4()
    res = client.get(f"/api/v1/resources/{fake_id}")
    assert res.status_code == 404
