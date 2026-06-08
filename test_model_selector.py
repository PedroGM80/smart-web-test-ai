"""
Tests for ModelSelector selection logic (no LLM instantiation needed).
"""

import pytest
from model_selector import ModelSelector, get_model_for_task


def test_default_mode_is_balanced():
    s = ModelSelector()
    assert s.mode == "balanced"


def test_invalid_mode_falls_back_to_balanced_config():
    s = ModelSelector(mode="nonexistent")
    balanced = ModelSelector(mode="balanced")
    assert s.config == balanced.config


def test_select_returns_a_model_string():
    s = ModelSelector(mode="speed")
    assert isinstance(s.select("analysis"), str)
    assert s.select("analysis")


def test_select_unknown_task_defaults_to_mistral():
    s = ModelSelector(mode="balanced")
    assert s.select("does-not-exist") == "mistral"


def test_set_model_overrides_selection():
    s = ModelSelector(mode="balanced")
    s.set_model("analysis", "custom-model")
    assert s.select("analysis") == "custom-model"


def test_modes_can_differ():
    speed = ModelSelector(mode="speed").select("analysis")
    quality = ModelSelector(mode="quality").select("analysis")
    # Both are valid strings; presets exist for each mode
    assert speed and quality


def test_info_reports_mode_and_config():
    s = ModelSelector(mode="quality")
    info = s.info()
    assert info["mode"] == "quality"
    assert "config" in info


def test_helper_get_model_for_task():
    assert isinstance(get_model_for_task("analysis", mode="speed"), str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
