import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from app.db.mongo import get_db
from app.main import app
from app.services import rag


@pytest.fixture()
def client(monkeypatch):
    db = AsyncMongoMockClient()["test"]
    app.dependency_overrides[get_db] = lambda: db

    async def fake_answer(q, history):
        return f"echo: {q}", []

    monkeypatch.setattr(rag, "answer", fake_answer)
    yield TestClient(app)
    app.dependency_overrides.clear()


def register(c, email="a@test.com"):
    r = c.post("/api/auth/register", json={"name": "A", "email": email, "password": "password123",
                                           "confirm_password": "password123"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_auth(client):
    h = register(client)
    assert client.get("/api/auth/me", headers=h).json()["email"] == "a@test.com"
    dup = client.post("/api/auth/register", json={"name": "A", "email": "A@test.com", "password": "password123",
                                                  "confirm_password": "password123"})
    assert dup.status_code == 409
    bad = client.post("/api/auth/register", json={"name": "A", "email": "b@test.com", "password": "password123",
                                                  "confirm_password": "nope"})
    assert bad.status_code == 422
    assert client.post("/api/auth/login", json={"email": "a@test.com", "password": "wrongpass"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "a@test.com", "password": "password123"}).status_code == 200
    assert client.get("/api/conversations").status_code == 401


def test_conversation_ownership(client):
    a, b = register(client, "a@test.com"), register(client, "b@test.com")
    cid = client.post("/api/conversations", headers=a).json()["id"]
    assert client.get(f"/api/conversations/{cid}", headers=b).status_code == 404
    assert client.patch(f"/api/conversations/{cid}", json={"title": "x"}, headers=b).status_code == 404
    assert client.delete(f"/api/conversations/{cid}", headers=b).status_code == 404
    assert client.post(f"/api/conversations/{cid}/messages", json={"content": "hi"}, headers=b).status_code == 404
    assert client.get("/api/conversations", headers=b).json() == []
    assert client.delete(f"/api/conversations/{cid}", headers=a).status_code == 204
    assert client.get(f"/api/conversations/{cid}", headers=a).status_code == 404


def test_chat_persistence(client):
    h = register(client)
    cid = client.post("/api/conversations", headers=h).json()["id"]
    r = client.post(f"/api/conversations/{cid}/messages", json={"content": "Explain decorators"}, headers=h)
    assert r.status_code == 200 and r.json()["assistant_message"]["content"] == "echo: Explain decorators"
    d = client.get(f"/api/conversations/{cid}", headers=h).json()
    assert [m["role"] for m in d["messages"]] == ["user", "assistant"]
    assert d["conversation"]["title"] == "Explain decorators"
