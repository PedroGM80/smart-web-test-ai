"""
Tests for the observe -> act -> re-observe loop (agent._run_steps).

This is the multi-step capability: when actions navigate to a new page, the
agent must re-analyze the new DOM and generate fresh actions for it, instead
of acting blind. Page, LLM and phases are mocked; no browser/Ollama.
"""

import pytest
from unittest.mock import MagicMock
import agent
from agent import SmartTestAgent


@pytest.fixture
def a(monkeypatch):
    monkeypatch.setattr(agent, "OllamaLLM", MagicMock())
    monkeypatch.setattr(agent, "sync_playwright", MagicMock())
    ag = SmartTestAgent(model="m", vision_model="v")
    # Common stubs
    ag.analyze_page = MagicMock(return_value={"html_analysis": "x"})
    ag.generate_test_plan = MagicMock(return_value="plan")
    return ag


def _page(url="https://site.com"):
    p = MagicMock()
    p.url = url
    return p


def test_single_page_runs_one_step(a):
    a.generate_actions = MagicMock(return_value=[{"locator": "#x", "action": "click", "value": None}])
    a.execute_actions = MagicMock(return_value={"total": 1, "passed": 1, "failed": 0,
                                                "errors": [], "navigated": False})
    run = a._run_steps(_page(), "https://site.com", "obj", max_steps=3)

    assert run["execution"]["steps"] == 1
    assert a.analyze_page.call_count == 1          # observed once
    assert run["execution"]["passed"] == 1


def test_navigation_triggers_reobservation(a):
    a.generate_actions = MagicMock(return_value=[{"locator": "#x", "action": "click", "value": None}])
    # First execution navigates, second doesn't
    a.execute_actions = MagicMock(side_effect=[
        {"total": 2, "passed": 2, "failed": 0, "errors": [], "navigated": True},
        {"total": 1, "passed": 1, "failed": 0, "errors": [], "navigated": False},
    ])
    run = a._run_steps(_page(), "https://site.com", "obj", max_steps=3)

    assert run["execution"]["steps"] == 2
    assert a.analyze_page.call_count == 2          # re-observed after navigating
    assert a.generate_test_plan.call_count == 2    # re-planned for the new page
    # Aggregation across steps
    assert run["execution"]["total"] == 3
    assert run["execution"]["passed"] == 3


def test_max_steps_caps_the_loop(a):
    a.generate_actions = MagicMock(return_value=[{"locator": "#x", "action": "click", "value": None}])
    # Always navigates -> would loop forever without the cap
    a.execute_actions = MagicMock(return_value={"total": 1, "passed": 1, "failed": 0,
                                                "errors": [], "navigated": True})
    run = a._run_steps(_page(), "https://site.com", "obj", max_steps=3)

    assert run["execution"]["steps"] == 3
    assert a.execute_actions.call_count == 3


def test_no_actions_stops_loop(a):
    a.generate_actions = MagicMock(return_value=[])
    a.execute_actions = MagicMock()
    run = a._run_steps(_page(), "https://site.com", "obj", max_steps=3)

    a.execute_actions.assert_not_called()
    assert run["execution"]["total"] == 0


def test_errors_aggregate_across_steps(a):
    a.generate_actions = MagicMock(return_value=[{"locator": "#x", "action": "click", "value": None}])
    a.execute_actions = MagicMock(side_effect=[
        {"total": 1, "passed": 0, "failed": 1,
         "errors": [{"action": "click:#x", "error": "e1"}], "navigated": True},
        {"total": 1, "passed": 0, "failed": 1,
         "errors": [{"action": "click:#y", "error": "e2"}], "navigated": False},
    ])
    run = a._run_steps(_page(), "https://site.com", "obj", max_steps=3)

    assert run["execution"]["failed"] == 2
    assert len(run["execution"]["errors"]) == 2


def test_first_plan_is_kept_in_result(a):
    a.generate_test_plan = MagicMock(side_effect=["initial plan", "continuation plan"])
    a.generate_actions = MagicMock(return_value=[{"locator": "#x", "action": "click", "value": None}])
    a.execute_actions = MagicMock(side_effect=[
        {"total": 1, "passed": 1, "failed": 0, "errors": [], "navigated": True},
        {"total": 1, "passed": 1, "failed": 0, "errors": [], "navigated": False},
    ])
    run = a._run_steps(_page(), "https://site.com", "obj", max_steps=3)
    assert run["plan"] == "initial plan"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
