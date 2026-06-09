"""
Fake agent for dry-run mode.

Produces a valid test report with the same contract as SmartTestAgent
(pass_rate, duration, total/passed/failed_actions, status) WITHOUT Ollama or
Playwright. This lets the full flow (run -> persist -> history/dashboard/API)
be exercised, demoed and tested end to end without the heavy AI stack.

Results are deterministic for a given URL+objective so behaviour is testable.
"""

import time
from datetime import datetime
from hashlib import sha256


class FakeAgent:
    """Drop-in stand-in for SmartTestAgent used by --dry-run."""

    def __init__(self, model: str = "fake", vision_model: str = "fake"):
        self.model = model
        self.vision_model = vision_model

    def test_web(self, url: str, objectives: str, headless: bool = True,
                 generate_cucumber: bool = False) -> dict:
        # Deterministic pseudo-result derived from the inputs
        seed = int(sha256(f"{url}|{objectives}".encode()).hexdigest(), 16)
        total = 5 + (seed % 6)            # 5..10 actions
        failed = seed % 3                 # 0..2 failures
        passed = total - failed
        pass_rate = round(passed / total * 100, 1)
        duration = round(1.0 + (seed % 50) / 10, 1)

        return {
            "url": url,
            "objectives": objectives,
            "objective": objectives,
            "plan": f"[dry-run] simulated plan for: {objectives}",
            "actions_total": total,
            "execution": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": [],
            },
            "validation": "dry-run: simulated validation passed",
            "results_log": [],
            "timestamp": datetime.now().isoformat(),
            "status": "success" if failed == 0 else "failure",
            "pass_rate": pass_rate,
            "duration": duration,
            "total_actions": total,
            "passed_actions": passed,
            "failed_actions": failed,
            "dry_run": True,
        }
