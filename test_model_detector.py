"""
Tests for ModelDetector - subprocess (ollama list) is mocked.
"""

import subprocess
import pytest
from unittest.mock import MagicMock
import model_detector
from model_detector import ModelDetector


def _mock_run(monkeypatch, stdout="", returncode=0, exc=None):
    def fake_run(*a, **k):
        if exc:
            raise exc
        return MagicMock(returncode=returncode, stdout=stdout)
    monkeypatch.setattr(model_detector.subprocess, "run", fake_run)


OLLAMA_LIST = "NAME            ID    SIZE   MODIFIED\nmistral:latest  abc   4GB    1 day ago\nllava:latest    def   5GB    2 days ago\n"


def test_detects_models(monkeypatch):
    _mock_run(monkeypatch, stdout=OLLAMA_LIST)
    d = ModelDetector()
    assert "mistral:latest" in d.get_available_models()
    assert "llava:latest" in d.get_available_models()


def test_has_model_partial_match(monkeypatch):
    _mock_run(monkeypatch, stdout=OLLAMA_LIST)
    d = ModelDetector()
    assert d.has_model("mistral") is True
    assert d.has_model("nonexistent") is False


def test_ollama_not_running_returns_empty(monkeypatch):
    _mock_run(monkeypatch, stdout="", returncode=1)
    d = ModelDetector()
    assert d.get_available_models() == []


def test_ollama_not_installed_returns_empty(monkeypatch):
    _mock_run(monkeypatch, exc=FileNotFoundError())
    d = ModelDetector()
    assert d.get_available_models() == []


def test_timeout_returns_empty(monkeypatch):
    _mock_run(monkeypatch, exc=subprocess.TimeoutExpired(cmd="ollama", timeout=5))
    d = ModelDetector()
    assert d.get_available_models() == []


def test_suggest_optimal_config_returns_dict(monkeypatch):
    _mock_run(monkeypatch, stdout=OLLAMA_LIST)
    d = ModelDetector()
    config = d.suggest_optimal_config()
    assert isinstance(config, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
