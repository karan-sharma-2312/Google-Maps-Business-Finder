"""API tests for system and statistics routes."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/system/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_statistics_summary_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/statistics/summary")

    assert response.status_code == 200
    payload = response.json()
    assert "total_searches" in payload
    assert "total_exports" in payload
    assert "total_discovered" in payload
