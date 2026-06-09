"""
Tests for agent.generate_actions - the LLM response parser.

This is the critical path that turns the model's free-text answer into
structured Playwright actions. The LLM is mocked, so no Ollama needed.
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


def _analysis():
    return {"html_analysis": "some html analysis text"}


def test_parses_well_formed_lines(a):
    a.llm.invoke = lambda prompt: (
        'input[name="search"]|fill|test query\n'
        'button:has-text("Search")|click|\n'
        '.error-message|check|'
    )
    actions = a.generate_actions("plan", _analysis())
    assert len(actions) == 3
    assert actions[0] == {"locator": 'input[name="search"]', "action": "fill", "value": "test query"}
    assert actions[1]["action"] == "click"
    assert actions[1]["value"] == ""


def test_skips_explanations_and_blank_lines(a):
    a.llm.invoke = lambda prompt: (
        "Here are the actions you asked for:\n"
        "\n"
        "input#q|fill|hello\n"
        "That should cover it."
    )
    actions = a.generate_actions("plan", _analysis())
    # Only the line containing '|' is kept
    assert len(actions) == 1
    assert actions[0]["locator"] == "input#q"


def test_empty_response_yields_no_actions(a):
    a.llm.invoke = lambda prompt: ""
    assert a.generate_actions("plan", _analysis()) == []


def test_line_without_pipe_is_ignored(a):
    a.llm.invoke = lambda prompt: "just some prose without a pipe"
    assert a.generate_actions("plan", _analysis()) == []


def test_value_is_optional(a):
    a.llm.invoke = lambda prompt: ".btn|click"
    actions = a.generate_actions("plan", _analysis())
    assert actions[0]["value"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
