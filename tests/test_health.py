from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "jobfit-api"
    assert payload["version"] == "2.0.0"


def test_dashboard_is_available():
    response = client.get("/")
    assert response.status_code == 200
    assert "JobFit" in response.text


def test_api_info():
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"
