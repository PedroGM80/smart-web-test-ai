"""
Tests for the agent report contract.

agent.test_web() is what every interface persists. These tests verify the
report exposes the fields the API/CLI/UI consume (pass_rate, duration,
total/passed/failed_actions, status) with values derived from the run -- not
the hard-coded defaults that previously masked a broken contract.

Playwright, the LLM and the analysis phases are mocked, so this runs without a
browser or Ollama.
"""

import pytest
from unittest.mock import MagicMock
import agent
from agent import SmartTestAgent


@pytest.fixture
def mocked_agent(monkeypatch):
    # Allow instantiation without the AI stack / browser
    monkeypatch.setattr(agent, "OllamaLLM", MagicMock())
    monkeypatch.setattr(agent, "sync_playwright", MagicMock())

    a = SmartTestAgent(model="mistral", vision_model="llava")

    # Stub the phases so test_web only exercises report assembly
    monkeypatch.setattr(a, "analyze_page", lambda page, url: {"elements": []})
    monkeypatch.setattr(a, "generate_test_plan", lambda url, obj, an: "plan")
    monkeypatch.setattr(a, "generate_actions", lambda plan, an: [{"locator": "x", "action": "click"}] * 4)
    monkeypatch.setattr(a, "final_validation", lambda page: "ok")
    monkeypatch.setattr(a, "_save_report", lambda report: None)
    monkeypatch.setattr(a, "_print_summary", lambda report: None)
    return a


def test_report_exposes_consumed_contract(mocked_agent):
    mocked_agent.execute_actions = lambda page, actions: {
        "total": 4, "passed": 3, "failed": 1, "errors": []
    }
    report = mocked_agent.test_web("https://x.com", "obj")

    # All keys the rest of the app reads must be present
    for key in ["pass_rate", "duration", "status",
                "total_actions", "passed_actions", "failed_actions"]:
        assert key in report, f"missing contract key: {key}"


def test_pass_rate_computed_from_execution(mocked_agent):
    mocked_agent.execute_actions = lambda page, actions: {
        "total": 4, "passed": 3, "failed": 1, "errors": []
    }
    report = mocked_agent.test_web("https://x.com", "obj")
    assert report["pass_rate"] == 75.0
    assert report["total_actions"] == 4
    assert report["passed_actions"] == 3
    assert report["failed_actions"] == 1
    assert report["status"] == "failure"


def test_all_passed_is_success(mocked_agent):
    mocked_agent.execute_actions = lambda page, actions: {
        "total": 2, "passed": 2, "failed": 0, "errors": []
    }
    report = mocked_agent.test_web("https://x.com", "obj")
    assert report["pass_rate"] == 100.0
    assert report["status"] == "success"


def test_no_actions_does_not_divide_by_zero(mocked_agent):
    mocked_agent.execute_actions = lambda page, actions: {
        "total": 0, "passed": 0, "failed": 0, "errors": []
    }
    report = mocked_agent.test_web("https://x.com", "obj")
    assert report["pass_rate"] == 0.0


def test_duration_is_present_and_numeric(mocked_agent):
    mocked_agent.execute_actions = lambda page, actions: {
        "total": 1, "passed": 1, "failed": 0, "errors": []
    }
    report = mocked_agent.test_web("https://x.com", "obj")
    assert isinstance(report["duration"], (int, float))
    assert report["duration"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
