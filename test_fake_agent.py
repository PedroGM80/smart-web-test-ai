"""
Tests for the dry-run FakeAgent and the end-to-end flow it enables
(run -> persist -> read back), all without Ollama/Playwright.
"""

import pytest
from fake_agent import FakeAgent
from smart_test import persist_report
from database import Base, create_db_engine, create_session_factory
from repositories import TestRepository


def test_report_has_full_contract():
    report = FakeAgent().test_web("https://example.com", "obj")
    for key in ["pass_rate", "duration", "status", "total_actions",
                "passed_actions", "failed_actions"]:
        assert key in report


def test_pass_rate_is_consistent_with_actions():
    report = FakeAgent().test_web("https://example.com", "obj")
    expected = round(report["passed_actions"] / report["total_actions"] * 100, 1)
    assert report["pass_rate"] == expected


def test_deterministic_for_same_input():
    a = FakeAgent().test_web("https://x.com", "same")
    b = FakeAgent().test_web("https://x.com", "same")
    assert a["pass_rate"] == b["pass_rate"]
    assert a["total_actions"] == b["total_actions"]


def test_different_inputs_can_differ():
    a = FakeAgent().test_web("https://a.com", "o")
    b = FakeAgent().test_web("https://b.com", "o")
    # Not guaranteed different, but both must be valid pass rates
    assert 0 <= a["pass_rate"] <= 100
    assert 0 <= b["pass_rate"] <= 100


def test_status_matches_failures():
    report = FakeAgent().test_web("https://x.com", "o")
    if report["failed_actions"] == 0:
        assert report["status"] == "success"
    else:
        assert report["status"] == "failure"


def test_end_to_end_run_persists_and_reads_back():
    # Full flow with a fake agent and an in-memory repository
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    repo = TestRepository(create_session_factory(engine))

    report = FakeAgent().test_web("https://example.com", "Verify load")
    persist_report(repo, url="https://example.com", objective="Verify load",
                   model="fake", report=report)

    stored = repo.list_chronological()
    assert len(stored) == 1
    assert stored[0].url == "https://example.com"
    assert stored[0].pass_rate == report["pass_rate"]
    engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
