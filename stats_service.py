"""
Stats Service - Single source of truth for test statistics calculation.

Both the database layer and the CLI used to compute averages, min/max and
success/failure counts independently. This service centralizes that logic so
there is one implementation, working on plain numbers regardless of where the
data comes from (ORM objects, dicts, etc). Callers extract the values; this
service does the maths.
"""

from typing import List, Optional, Dict


class StatsService:
    """Pure statistics calculations over test records."""

    @staticmethod
    def summarize(
        pass_rates: List[float],
        durations: List[float],
        statuses: Optional[List[str]] = None,
    ) -> Dict:
        """Compute summary statistics from already-extracted values.

        Args:
            pass_rates: list of pass-rate values.
            durations: list of duration values.
            statuses: optional list of status strings ("success"/"failure").

        Returns:
            Dict with total_tests, avg_pass_rate, avg_duration, min_pass_rate,
            max_pass_rate, success_count, failure_count.
        """
        total = len(pass_rates)

        if total == 0:
            return {
                "total_tests": 0,
                "avg_pass_rate": 0,
                "avg_duration": 0,
                "min_pass_rate": 0,
                "max_pass_rate": 0,
                "success_count": 0,
                "failure_count": 0,
            }

        success_count = 0
        failure_count = 0
        if statuses is not None:
            normalized = [str(s).lower() for s in statuses]
            success_count = sum(1 for s in normalized if s == "success")
            failure_count = sum(1 for s in normalized if s == "failure")

        return {
            "total_tests": total,
            "avg_pass_rate": sum(pass_rates) / total,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_pass_rate": min(pass_rates),
            "max_pass_rate": max(pass_rates),
            "success_count": success_count,
            "failure_count": failure_count,
        }
