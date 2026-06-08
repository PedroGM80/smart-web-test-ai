"""
Tests for the FastAPI layer - verifies persistence goes through the repository.
The real agent (Ollama + Playwright) is mocked so we test the API/persistence
wiring, not the browser automation.
"""

import pytest
from fastapi.testclient import TestClient

import api
from api import app, get_repository
from database import Base, create_db_engine, create_session_factory
from repositories import TestRepository


@pytest.fixture
def client(monkeypatch):
    # Isolated in-memory repository injected via dependency override
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    repo = TestRepository(create_session_factory(engine))
    app.dependency_overrides[get_repository] = lambda: repo

    # Mock the agent and model selector so no Ollama/Playwright is needed
    class FakeAgent:
        def __init__(self, *a, **k):
            pass
        def test_web(self, **k):
            return {"pass_rate": 92.0, "total_actions": 10,
                    "passed_actions": 9, "failed_actions": 1, "duration": 12.5}

    class FakeSelector:
        def __init__(self, *a, **k):
            pass
        def select(self, _kind):
            return "mistral"

    monkeypatch.setattr(api, "SmartTestAgent", FakeAgent)
    monkeypatch.setattr(api, "ModelSelector", FakeSelector)

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _run_test(client, url="https://github.com", objective="Test repo", mode="balanced"):
    return client.post("/test", json={"url": url, "objective": objective, "mode": mode})


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_execute_test_persists(client):
    r = _run_test(client)
    assert r.status_code == 200
    body = r.json()
    assert body["pass_rate"] == 92.0
    assert body["url"] == "https://github.com"

    # The result must now be retrievable from the database
    results = client.get("/results").json()
    assert results["total"] == 1
    assert results["results"][0]["url"] == "https://github.com"


def test_results_empty(client):
    results = client.get("/results").json()
    assert results["total"] == 0
    assert results["results"] == []


def test_get_result_by_id(client):
    _run_test(client)
    # First record has id 1
    r = client.get("/results/1")
    assert r.status_code == 200
    assert r.json()["url"] == "https://github.com"


def test_get_result_not_found(client):
    r = client.get("/results/999")
    assert r.status_code == 404


def test_stats_from_database(client):
    _run_test(client, mode="speed")
    _run_test(client, mode="balanced")

    stats = client.get("/stats").json()
    assert stats["total_tests"] == 2
    assert stats["avg_pass_rate"] == 92.0
    assert stats["by_mode"]["speed"]["count"] == 1
    assert stats["by_mode"]["balanced"]["count"] == 1


def test_invalid_url_rejected(client):
    r = client.post("/test", json={"url": "ftp://bad", "objective": "x"})
    assert r.status_code == 400


def test_missing_objective_rejected(client):
    r = client.post("/test", json={"url": "https://x.com", "objective": ""})
    assert r.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
