import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import app
from backend.app.models.conversation import Conversation
from backend.app.models.conversation_message import ConversationMessage

client = TestClient(app)


@pytest.fixture
def auth_learner_a():
    """Register and authenticate test learner A."""
    email = f"asst_learner_a_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "Assistant Learner A",
        "email": email,
        "password": "Password123!"
    })
    data = r.json()["data"]
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user_id": uuid.UUID(data["user"]["id"]),
        "email": email
    }


@pytest.fixture
def auth_learner_b():
    """Register and authenticate test learner B for cross-user isolation tests."""
    email = f"asst_learner_b_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "Assistant Learner B",
        "email": email,
        "password": "Password123!"
    })
    data = r.json()["data"]
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user_id": uuid.UUID(data["user"]["id"]),
        "email": email
    }


def test_assistant_chat_new_conversation(auth_learner_a):
    """Test 1: Sending message without conversation_id creates a new conversation with grounded answer."""
    headers = auth_learner_a["headers"]
    payload = {"message": "How do I reduce overfitting in machine learning models?"}

    r = client.post("/api/v1/assistant/chat", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()["data"]

    assert data["conversation_id"] is not None
    assert data["message"]["role"] == "assistant"
    assert len(data["message"]["content"]) > 10
    assert len(data["sources"]) > 0
    for s in data["sources"]:
        assert s["url"].startswith("http")


def test_assistant_chat_existing_conversation(auth_learner_a):
    """Test 2: Sending follow-up message with conversation_id appends messages sequentially."""
    headers = auth_learner_a["headers"]

    # First turn
    r1 = client.post("/api/v1/assistant/chat", json={"message": "What is Python?"}, headers=headers)
    assert r1.status_code == 200
    conv_id = r1.json()["data"]["conversation_id"]

    # Second turn
    r2 = client.post(
        "/api/v1/assistant/chat",
        json={"conversation_id": conv_id, "message": "What is FastAPI?"},
        headers=headers
    )
    assert r2.status_code == 200
    data2 = r2.json()["data"]
    assert data2["conversation_id"] == conv_id

    # Verify message history contains both user messages and both assistant responses
    r_detail = client.get(f"/api/v1/assistant/conversations/{conv_id}", headers=headers)
    assert r_detail.status_code == 200
    messages = r_detail.json()["data"]["messages"]
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[2]["role"] == "user"
    assert messages[3]["role"] == "assistant"


def test_list_conversations_and_pagination(auth_learner_a):
    """Test 3: GET /api/v1/assistant/conversations returns paginated summaries."""
    headers = auth_learner_a["headers"]

    # Create 3 conversations
    for i in range(3):
        client.post("/api/v1/assistant/chat", json={"message": f"Question number {i+1}?"}, headers=headers)

    r_list = client.get("/api/v1/assistant/conversations?page=1&page_size=2", headers=headers)
    assert r_list.status_code == 200
    data = r_list.json()["data"]
    assert len(data) == 2
    assert "message_count" in data[0]


def test_cross_user_conversation_isolation(auth_learner_a, auth_learner_b):
    """Test 4: Learner B cannot access or append messages to Learner A's conversation."""
    headers_a = auth_learner_a["headers"]
    headers_b = auth_learner_b["headers"]

    # User A creates a conversation
    r_a = client.post("/api/v1/assistant/chat", json={"message": "Secret study question from User A"}, headers=headers_a)
    conv_id_a = r_a.json()["data"]["conversation_id"]

    # User B attempts to view User A's conversation detail -> 403 Forbidden
    r_b_view = client.get(f"/api/v1/assistant/conversations/{conv_id_a}", headers=headers_b)
    assert r_b_view.status_code in [403, 404]

    # User B attempts to append message to User A's conversation -> 403 Forbidden
    r_b_chat = client.post(
        "/api/v1/assistant/chat",
        json={"conversation_id": conv_id_a, "message": "Injected message from User B"},
        headers=headers_b
    )
    assert r_b_chat.status_code in [403, 404]


def test_unauthenticated_assistant_rejected():
    """Test 5: Unauthenticated chat or conversation requests are rejected with HTTP 401."""
    r_chat = client.post("/api/v1/assistant/chat", json={"message": "Hello"})
    assert r_chat.status_code == 401

    r_list = client.get("/api/v1/assistant/conversations")
    assert r_list.status_code == 401


def test_validation_errors_on_empty_message(auth_learner_a):
    """Test 6: Empty or whitespace message returns HTTP 422."""
    headers = auth_learner_a["headers"]

    r_empty = client.post("/api/v1/assistant/chat", json={"message": ""}, headers=headers)
    assert r_empty.status_code == 422

    r_invalid_uuid = client.post(
        "/api/v1/assistant/chat",
        json={"conversation_id": "not-a-uuid", "message": "Valid question"},
        headers=headers
    )
    assert r_invalid_uuid.status_code == 422
