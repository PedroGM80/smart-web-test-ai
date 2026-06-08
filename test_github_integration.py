"""
Tests for GitHubIssueCreator - HTTP mocked, no network/token needed.
"""

import pytest
from unittest.mock import MagicMock
import github_integration
from github_integration import GitHubIssueCreator


@pytest.fixture
def creator():
    return GitHubIssueCreator(repo="owner/repo", token="ghp_dummy")


@pytest.fixture
def post_mock(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(github_integration, "requests", MagicMock(post=mock))
    return mock


def test_labels_always_include_base(creator):
    labels = creator._determine_labels({"pass_rate": 100})
    assert "smart-test" in labels
    assert "automated" in labels


def test_labels_critical_below_50(creator):
    assert "critical" in creator._determine_labels({"pass_rate": 30})


def test_labels_bug_between_50_and_75(creator):
    labels = creator._determine_labels({"pass_rate": 60})
    assert "bug" in labels
    assert "critical" not in labels


def test_labels_clean_when_high(creator):
    labels = creator._determine_labels({"pass_rate": 95})
    assert "critical" not in labels
    assert "bug" not in labels


def test_create_issue_success_returns_url(creator, post_mock):
    post_mock.return_value = MagicMock(
        status_code=201, json=lambda: {"html_url": "https://github.com/owner/repo/issues/1"}
    )
    url = creator._create_issue({"title": "x", "body": "y"})
    assert url == "https://github.com/owner/repo/issues/1"


def test_create_issue_failure_returns_none(creator, post_mock):
    post_mock.return_value = MagicMock(status_code=422, text="bad")
    assert creator._create_issue({"title": "x"}) is None


def test_create_issue_network_error_returns_none(creator, post_mock):
    post_mock.side_effect = Exception("boom")
    assert creator._create_issue({"title": "x"}) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
