"""
Tests for ModelLearner - learning data stored in a temp JSON, no Ollama needed.
"""

import pytest
from model_learner import ModelLearner


@pytest.fixture
def learner(tmp_path, monkeypatch):
    monkeypatch.setattr(ModelLearner, "LEARNING_FILE", str(tmp_path / "learning.json"))
    return ModelLearner()


def test_starts_empty(learner):
    stats = learner.get_stats()
    assert stats["total_runs"] == 0
    assert stats["domains_learned"] == 0


def test_record_result_increments_runs(learner):
    learner.record_result("https://github.com", "mistral", "analysis",
                          duration=10.0, success=True, tokens=100)
    stats = learner.get_stats()
    assert stats["total_runs"] == 1
    assert stats["domains_learned"] == 1


def test_record_tracks_domain(learner):
    learner.record_result("https://github.com/x", "mistral", "analysis",
                          duration=5.0, success=True)
    assert "github.com" in learner.get_stats()["by_domain"]


def test_multiple_records_accumulate(learner):
    for i in range(3):
        learner.record_result(f"https://site{i}.com", "mistral", "analysis",
                              duration=5.0, success=True)
    assert learner.get_stats()["total_runs"] == 3
    assert learner.get_stats()["domains_learned"] == 3


def test_recommend_returns_string_or_none(learner):
    learner.record_result("https://github.com", "mistral", "analysis",
                          duration=5.0, success=True)
    rec = learner.recommend_model(url="https://github.com", task="analysis")
    assert rec is None or isinstance(rec, str)


def test_data_persists_across_instances(tmp_path, monkeypatch):
    path = str(tmp_path / "learning.json")
    monkeypatch.setattr(ModelLearner, "LEARNING_FILE", path)
    l1 = ModelLearner()
    l1.record_result("https://github.com", "mistral", "analysis",
                     duration=5.0, success=True)
    # New instance should load the saved data
    l2 = ModelLearner()
    assert l2.get_stats()["total_runs"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
