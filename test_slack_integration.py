"""
Tests for SlackNotifier - HTTP is mocked, no network needed.
"""

import pytest
from unittest.mock import MagicMock
import slack_integration
from slack_integration import SlackNotifier


@pytest.fixture
def post_mock(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(slack_integration, "requests", MagicMock(post=mock))
    return mock


def _result():
    return {"url": "https://github.com", "pass_rate": 92.0, "duration": 12.5,
            "status": "success", "mode": "balanced"}


def test_no_webhook_returns_false(post_mock, monkeypatch):
    # Ensure no .env webhook is picked up
    monkeypatch.setattr(SlackNotifier, "_load_webhook_from_env", lambda self: None)
    notifier = SlackNotifier(webhook_url=None)
    assert notifier.send_test_result(_result()) is False
    post_mock.assert_not_called()


def test_successful_send(post_mock):
    post_mock.return_value = MagicMock(status_code=200)
    notifier = SlackNotifier(webhook_url="https://hooks.slack.com/x")
    assert notifier.send_test_result(_result()) is True
    post_mock.assert_called_once()


def test_payload_contains_url(post_mock):
    post_mock.return_value = MagicMock(status_code=200)
    notifier = SlackNotifier(webhook_url="https://hooks.slack.com/x")
    notifier.send_test_result(_result())
    _, kwargs = post_mock.call_args
    payload = str(kwargs.get("json", ""))
    assert "github.com" in payload


def test_non_200_returns_false(post_mock):
    post_mock.return_value = MagicMock(status_code=500)
    notifier = SlackNotifier(webhook_url="https://hooks.slack.com/x")
    assert notifier.send_test_result(_result()) is False


def test_network_error_returns_false(post_mock):
    post_mock.side_effect = Exception("connection refused")
    notifier = SlackNotifier(webhook_url="https://hooks.slack.com/x")
    assert notifier.send_test_result(_result()) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
