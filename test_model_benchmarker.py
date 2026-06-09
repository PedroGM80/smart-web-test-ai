"""
Tests for ModelBenchmarker - LLM mocked, no Ollama. Covers metric computation.
"""

from unittest.mock import MagicMock
import model_benchmarker
from model_benchmarker import ModelBenchmarker


def _with_llm(monkeypatch, invoke):
    fake_cls = MagicMock()
    fake_cls.return_value = MagicMock(invoke=invoke)
    monkeypatch.setattr(model_benchmarker, "OllamaLLM", fake_cls)


def test_benchmark_model_computes_metrics(monkeypatch):
    _with_llm(monkeypatch, invoke=lambda *a, **k: "one two three four five")
    b = ModelBenchmarker()
    result = b.benchmark_model("mistral")

    assert result["model"] == "mistral"
    assert result["tests"]  # at least one test ran
    for test in result["tests"].values():
        if test["status"] == "✓":
            assert test["tokens"] == 5
            assert test["tokens_per_second"] >= 0
            assert "time_seconds" in test


def test_benchmark_model_records_errors(monkeypatch):
    def boom(*a, **k):
        raise Exception("model crashed")
    _with_llm(monkeypatch, invoke=boom)
    b = ModelBenchmarker()
    result = b.benchmark_model("mistral")

    for test in result["tests"].values():
        assert test["status"] == "✗"
        assert "model crashed" in test["error"]


def test_benchmark_models_aggregates(monkeypatch):
    _with_llm(monkeypatch, invoke=lambda *a, **k: "a b c")
    b = ModelBenchmarker()
    results = b.benchmark_models(["mistral", "llava"])
    assert set(results.keys()) == {"mistral", "llava"}


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
