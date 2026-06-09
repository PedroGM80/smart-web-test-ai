"""
Tests for TestKnowledgeBase.

Covers the pure helpers and the degraded mode: when ChromaDB/Ollama are not
available, collection is None and the public methods must degrade cleanly
instead of crashing. In this environment ChromaDB isn't installed, so the
degraded path is exercised for real.
"""

import pytest
from knowledge_base import TestKnowledgeBase


@pytest.fixture
def kb():
    return TestKnowledgeBase()


def test_collection_none_without_chromadb(kb):
    # No ChromaDB installed -> degraded mode
    assert kb.collection is None


def test_extract_domain(kb):
    assert kb._extract_domain("https://github.com/user/repo") == "github.com"
    assert kb._extract_domain("http://example.org") == "example.org"


def test_extract_domain_handles_garbage(kb):
    # Should not raise
    assert isinstance(kb._extract_domain("not a url"), str)


def test_create_test_document_contains_fields(kb):
    doc = kb._create_test_document(
        url="https://github.com",
        objectives="login",
        plan="step 1",
        results={"total_actions": 5, "passed_actions": 4, "pass_rate": 80.0},
    )
    assert "https://github.com" in doc
    assert "login" in doc
    assert "80.0%" in doc


def test_store_test_degrades_to_false(kb):
    ok = kb.store_test("https://x.com", "obj", "plan", {"pass_rate": 90})
    assert ok is False


def test_find_similar_degrades_to_empty(kb):
    assert kb.find_similar_tests("https://x.com", "obj") == []


def test_domain_stats_degrades_to_empty(kb):
    assert kb.get_domain_statistics("github.com") == {}


def test_export_degrades_to_false(kb, tmp_path):
    assert kb.export_knowledge(str(tmp_path / "export.json")) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
