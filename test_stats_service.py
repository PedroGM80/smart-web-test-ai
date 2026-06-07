"""
Tests for StatsService
"""

import pytest
from stats_service import StatsService


class TestStatsService:
    """Test suite for the shared statistics service"""

    def test_empty(self):
        result = StatsService.summarize([], [])
        assert result["total_tests"] == 0
        assert result["avg_pass_rate"] == 0
        assert result["avg_duration"] == 0
        assert result["success_count"] == 0
        assert result["failure_count"] == 0

    def test_single_value(self):
        result = StatsService.summarize([90.0], [30.0])
        assert result["total_tests"] == 1
        assert result["avg_pass_rate"] == 90.0
        assert result["avg_duration"] == 30.0
        assert result["min_pass_rate"] == 90.0
        assert result["max_pass_rate"] == 90.0

    def test_multiple_values(self):
        result = StatsService.summarize([90.0, 95.0, 85.0], [30.0, 35.0, 25.0])
        assert result["total_tests"] == 3
        assert result["avg_pass_rate"] == pytest.approx(90.0)
        assert result["avg_duration"] == pytest.approx(30.0)
        assert result["min_pass_rate"] == 85.0
        assert result["max_pass_rate"] == 95.0

    def test_with_statuses(self):
        result = StatsService.summarize(
            [90.0, 50.0, 95.0],
            [30.0, 40.0, 35.0],
            statuses=["success", "failure", "success"],
        )
        assert result["success_count"] == 2
        assert result["failure_count"] == 1

    def test_statuses_case_insensitive(self):
        result = StatsService.summarize(
            [90.0, 50.0],
            [30.0, 40.0],
            statuses=["SUCCESS", "Failure"],
        )
        assert result["success_count"] == 1
        assert result["failure_count"] == 1

    def test_durations_empty_but_pass_rates_present(self):
        result = StatsService.summarize([90.0, 80.0], [])
        assert result["total_tests"] == 2
        assert result["avg_duration"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
