import os

os.environ.setdefault("SECRET_KEY", "test-only-secret")

from app import app


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_home():
    client = app.test_client()
    assert client.get("/").status_code == 200
