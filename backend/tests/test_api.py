import os
os.environ["DATABASE_URL"] = "sqlite:///./backend/test_sih26120.db"

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def token():
    r = client.post("/api/v1/auth/login", json={"username": "engineer", "password": "Engineer@26120"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in {"ok", "degraded"}


def test_login_and_wells():
    t = token()
    r = client.get("/api/v1/wells", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 1


def test_model_status():
    t = token()
    r = client.get("/api/v1/predict/model/status", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200, r.text
    assert "production" in r.json()
