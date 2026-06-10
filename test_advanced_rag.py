"""
Tests for AdvancedRAG - sklearn clustering + JSON data, no Ollama/ChromaDB.
"""

import pytest
from advanced_rag import AdvancedRAG
from model_learner import ModelLearner


@pytest.fixture
def rag(tmp_path, monkeypatch):
    monkeypatch.setattr(ModelLearner, "LEARNING_FILE", str(tmp_path / "learning.json"))
    monkeypatch.setattr(AdvancedRAG, "ADVANCED_DATA_FILE", str(tmp_path / "advanced.json"))
    return AdvancedRAG()


def _populate(rag, domains, success=True):
    for i, d in enumerate(domains):
        # Vary per-domain stats so KMeans actually has distinct points
        rag.learner.record_result(f"https://{d}", "mistral", "analysis",
                                   duration=2.0 + i * 4.0,
                                   success=(success if i % 2 == 0 else not success),
                                   tokens=30 + i * 40)
        if i % 2 == 0:
            rag.learner.record_result(f"https://{d}", "mistral", "analysis",
                                       duration=1.0 + i, success=True, tokens=20)


def test_predict_defects_unknown_domain(rag):
    result = rag.predict_defects("https://never-seen.com", "test")
    assert result["risk_level"] == "unknown"
    assert result["confidence"] == 0.0


def test_predict_defects_known_high_success(rag):
    _populate(rag, ["github.com"], success=True)
    result = rag.predict_defects("https://github.com", "test")
    assert result["risk_level"] in ("low", "medium", "high")
    assert 0.0 <= result["confidence"] <= 1.0


def test_cluster_domains_needs_three(rag):
    # Fewer than 3 domains must return {} gracefully (previously crashed with
    # TypeError because domains_learned is an int, not a list)
    _populate(rag, ["a.com", "b.com"])
    assert rag.cluster_domains() == {}


def test_cluster_domains_with_enough_data(rag):
    _populate(rag, ["a.com", "b.com", "c.com", "d.com"])
    clusters = rag.cluster_domains(n_clusters=2)
    assert isinstance(clusters, dict)
    # All clustered domains accounted for
    total = sum(len(v) for v in clusters.values())
    assert total == 4


def test_get_recommendations_returns_list(rag):
    _populate(rag, ["github.com"])
    recs = rag.get_recommendations("https://github.com", "test login")
    assert isinstance(recs, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_get_recommendations_with_clusters_does_not_crash(rag):
    # Regression: this path referenced an undefined 'stats' (NameError) when
    # clusters existed and the domain was unknown.
    _populate(rag, ["a.com", "b.com", "c.com", "d.com"])
    recs = rag.get_recommendations("https://never-seen-domain.com", "test")
    assert isinstance(recs, list)
