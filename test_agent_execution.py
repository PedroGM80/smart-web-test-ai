"""
Tests for agent.execute_actions - action execution and pass/fail counting.
Playwright page is mocked; no browser needed.
"""

import pytest
from unittest.mock import MagicMock
import agent
from agent import SmartTestAgent


@pytest.fixture
def a(monkeypatch):
    monkeypatch.setattr(agent, "OllamaLLM", MagicMock())
    monkeypatch.setattr(agent, "sync_playwright", MagicMock())
    return SmartTestAgent(model="m", vision_model="v")


def test_all_actions_pass(a):
    page = MagicMock()
    page.locator.return_value.is_visible.return_value = True
    actions = [
        {"locator": "#a", "action": "fill", "value": "x"},
        {"locator": "#b", "action": "click", "value": None},
        {"locator": "#c", "action": "hover", "value": None},
    ]
    res = a.execute_actions(page, actions)
    assert res["total"] == 3
    assert res["passed"] == 3
    assert res["failed"] == 0


def test_failing_action_is_counted(a):
    page = MagicMock()
    page.locator.return_value.click.side_effect = Exception("element not found")
    res = a.execute_actions(page, [{"locator": "#x", "action": "click", "value": None}])
    assert res["failed"] == 1
    assert res["passed"] == 0
    assert len(res["errors"]) == 1
    assert "element not found" in res["errors"][0]["error"]


def test_check_fails_when_not_visible(a):
    page = MagicMock()
    page.locator.return_value.is_visible.return_value = False
    res = a.execute_actions(page, [{"locator": "#x", "action": "check", "value": None}])
    assert res["failed"] == 1


def test_mixed_results(a):
    page = MagicMock()
    page.locator.return_value.is_visible.return_value = True
    # second action fails
    def locator(sel):
        m = MagicMock()
        if sel == "#bad":
            m.click.side_effect = Exception("boom")
        m.is_visible.return_value = True
        return m
    page.locator.side_effect = locator
    actions = [
        {"locator": "#good", "action": "click", "value": None},
        {"locator": "#bad", "action": "click", "value": None},
    ]
    res = a.execute_actions(page, actions)
    assert res["passed"] == 1
    assert res["failed"] == 1


def test_unknown_action_counts_as_failure(a):
    # An unrecognized action (an LLM might emit "type", "select", "press")
    # now counts as a failure with a clear error, instead of silently
    # distorting the pass rate.
    page = MagicMock()
    res = a.execute_actions(page, [{"locator": "#x", "action": "teleport", "value": None}])
    assert res["total"] == 1
    assert res["passed"] == 0
    assert res["failed"] == 1
    assert "Unknown action" in res["errors"][0]["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_press_action(a):
    page = MagicMock()
    page.url = "https://x.com"
    res = a.execute_actions(page, [{"locator": "#search", "action": "press", "value": "Enter"}])
    assert res["passed"] == 1
    page.locator.return_value.press.assert_called_with("Enter")


def test_select_action(a):
    page = MagicMock()
    page.url = "https://x.com"
    res = a.execute_actions(page, [{"locator": "#country", "action": "select", "value": "Spain"}])
    assert res["passed"] == 1
    page.locator.return_value.select_option.assert_called_with("Spain")


def test_goto_action(a):
    page = MagicMock()
    page.url = "https://x.com"
    res = a.execute_actions(page, [{"locator": "https://y.com", "action": "goto", "value": None}])
    assert res["passed"] == 1
    page.goto.assert_called_with("https://y.com")


def test_scroll_action(a):
    page = MagicMock()
    page.url = "https://x.com"
    res = a.execute_actions(page, [{"locator": "#footer", "action": "scroll", "value": None}])
    assert res["passed"] == 1


def test_navigated_flag_set_when_url_changes(a):
    page = MagicMock()
    urls = iter(["https://x.com", "https://x.com/results"])
    type(page).url = property(lambda self: next(urls))
    res = a.execute_actions(page, [{"locator": "#go", "action": "click", "value": None}])
    assert res["navigated"] is True


def test_navigated_flag_false_when_url_same(a):
    page = MagicMock()
    page.url = "https://x.com"
    res = a.execute_actions(page, [{"locator": "#btn", "action": "click", "value": None}])
    assert res["navigated"] is False
