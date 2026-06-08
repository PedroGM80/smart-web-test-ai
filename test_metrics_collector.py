"""
Tests for MetricsCollector report parsing - no InfluxDB needed.
"""

import json
import pytest
from metrics_collector import MetricsCollector


@pytest.fixture
def collector():
    # InfluxDB unavailable in tests; client falls back to None
    return MetricsCollector()


def test_client_is_none_without_influxdb(collector):
    assert collector.client is None


def test_calculate_pass_rate(collector):
    report = {"execution": {"total": 4, "passed": 3, "failed": 1}}
    assert collector._calculate_pass_rate(report) == 75.0


def test_calculate_pass_rate_zero_total(collector):
    report = {"execution": {"total": 0, "passed": 0}}
    assert collector._calculate_pass_rate(report) == 0


def test_check_validation_passed(collector):
    assert collector._check_validation({"validation": "All checks passed"}) is True
    assert collector._check_validation({"validation": "todo pasó bien"}) is True


def test_check_validation_failed(collector):
    assert collector._check_validation({"validation": "errors found"}) is False


def test_collect_from_report(tmp_path, collector):
    report = {
        "url": "https://github.com",
        "objectives": "test",
        "actions_total": 5,
        "execution": {"total": 5, "passed": 4, "failed": 1, "errors": [{"e": 1}]},
        "validation": "passed",
    }
    p = tmp_path / "report.json"
    p.write_text(json.dumps(report))

    metrics = collector.collect_from_report(str(p))
    assert metrics["url"] == "https://github.com"
    assert metrics["passed_actions"] == 4
    assert metrics["failed_actions"] == 1
    assert metrics["pass_rate"] == 80.0
    assert metrics["errors_count"] == 1


def test_collect_from_missing_file_returns_empty(collector):
    assert collector.collect_from_report("/nonexistent/report.json") == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
