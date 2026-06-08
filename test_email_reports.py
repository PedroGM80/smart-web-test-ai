"""
Tests for EmailReporter - SMTP mocked, no network/credentials needed.
"""

import pytest
from unittest.mock import MagicMock
import email_reports
from email_reports import EmailReporter


def _summary():
    return {"total_tests": 12, "avg_pass_rate": 88.5, "avg_duration": 30.0,
            "domains": 3, "best_model": "mistral", "total_time_saved": 7200}


@pytest.fixture
def reporter():
    return EmailReporter(sender_email="me@example.com", sender_password="secret")


def test_generate_html_contains_summary_values(reporter):
    html = reporter._generate_html(_summary(), ["team@example.com"])
    assert "88.5" in html          # avg_pass_rate
    assert "12" in html            # total_tests
    assert "mistral" in html       # best_model


def test_send_without_credentials_returns_false(monkeypatch):
    monkeypatch.setattr(EmailReporter, "_load_from_env", lambda self, key: None)
    r = EmailReporter(sender_email=None, sender_password=None)
    assert r.send_daily_report(["team@example.com"], _summary()) is False


def test_send_success(reporter, monkeypatch):
    monkeypatch.setattr(email_reports, "smtplib", MagicMock())
    assert reporter.send_daily_report(["team@example.com"], _summary()) is True


def test_send_smtp_error_returns_false(reporter, monkeypatch):
    fake_smtp = MagicMock()
    fake_smtp.SMTP.side_effect = Exception("smtp down")
    monkeypatch.setattr(email_reports, "smtplib", fake_smtp)
    assert reporter.send_daily_report(["team@example.com"], _summary()) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
