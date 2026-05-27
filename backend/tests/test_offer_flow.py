from fastapi.testclient import TestClient

from app.main import app
from app.services.member_store import member_store

client = TestClient(app)


def setup_function():
    member_store.clear()


def auth_headers() -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "demo123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_returns_access_token():
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "demo123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_offer_generation_requires_auth():
    response = client.post("/api/v1/offers", json={"member_id": "x"})
    assert response.status_code == 401


def test_offer_generation_persists_transaction():
    payload = {
        "member_id": "A0F18FAA",
        "transaction_type": "GIFT",
        "points_bought": 500,
        "revenue_usd": 25.5,
    }
    response = client.post("/api/v1/offers", json=payload, headers=auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["transaction"]["member_id"] == "A0F18FAA"
    assert data["offer"]["offer_code"]
    assert data["value_prediction"]["prediction"] >= 0

    history = client.get("/api/v1/members/A0F18FAA/transactions", headers=auth_headers())
    assert history.status_code == 200
    assert len(history.json()["transactions"]) == 1


def test_invalid_payload_returns_422_after_auth():
    response = client.post("/api/v1/offers", json={"member_id": "x"}, headers=auth_headers())
    assert response.status_code == 422
