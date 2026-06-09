"""
Tests for the environment doctor - all external checks are injected/mocked.
"""

from unittest.mock import MagicMock
import doctor


def test_python_version_ok():
    ok, msg = doctor.check_python_version(3, 9)
    assert ok is True


def test_python_version_too_old():
    ok, _ = doctor.check_python_version(99, 0)
    assert ok is False


def test_dependency_present():
    ok, _ = doctor.check_dependency("sys")
    assert ok is True


def test_dependency_missing():
    ok, msg = doctor.check_dependency("totally_not_a_real_module_xyz")
    assert ok is False
    assert "NOT installed" in msg


def test_ollama_installed_true():
    ok, _ = doctor.check_ollama_installed(which=lambda _: "/usr/bin/ollama")
    assert ok is True


def test_ollama_installed_false():
    ok, _ = doctor.check_ollama_installed(which=lambda _: None)
    assert ok is False


def test_ollama_models_all_present():
    runner = lambda: MagicMock(returncode=0, stdout="mistral:latest\nllava:latest\n")
    ok, _ = doctor.check_ollama_models(runner=runner)
    assert ok is True


def test_ollama_models_missing():
    runner = lambda: MagicMock(returncode=0, stdout="mistral:latest\n")
    ok, msg = doctor.check_ollama_models(runner=runner)
    assert ok is False
    assert "llava" in msg


def test_ollama_not_running():
    runner = lambda: MagicMock(returncode=1, stdout="")
    ok, msg = doctor.check_ollama_models(runner=runner)
    assert ok is False
    assert "not running" in msg


def test_ollama_not_installed():
    def runner():
        raise FileNotFoundError()
    ok, msg = doctor.check_ollama_models(runner=runner)
    assert ok is False


def test_database_check_ok():
    ok, _ = doctor.check_database()
    assert ok is True


def test_run_all_returns_every_check():
    results = doctor.run_all_checks()
    names = [r[0] for r in results]
    assert "python" in names
    assert "ollama" in names
    assert "playwright" in names
    # every result is (name, bool, message)
    for name, ok, msg in results:
        assert isinstance(ok, bool)
        assert isinstance(msg, str)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
