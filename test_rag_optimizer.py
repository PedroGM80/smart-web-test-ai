"""
Tests for RAGOptimizer - pure helpers and degraded mode (no Ollama/ChromaDB).
"""

import pytest
from rag_optimizer import RAGOptimizer
from knowledge_base import TestKnowledgeBase


@pytest.fixture
def opt():
    # Degraded knowledge base (no ChromaDB) injected
    return RAGOptimizer(knowledge_base=TestKnowledgeBase())


def test_llm_is_none_without_ollama(opt):
    assert opt.llm is None


def test_extract_domain(opt):
    assert opt._extract_domain("https://github.com/a/b") == "github.com"
    assert opt._extract_domain("http://example.org") == "example.org"


def test_find_common_patterns_detects_keywords(opt):
    tests = [
        {"document": "Se probó el formulario de login"},
        {"document": "Click en botón de enviar"},
        {"document": "campo de búsqueda validado"},
    ]
    patterns = opt._find_common_patterns(tests)
    assert "formulario" in patterns
    assert "botones" in patterns
    assert "búsqueda" in patterns


def test_find_common_patterns_empty(opt):
    assert opt._find_common_patterns([{"document": "nada relevante"}]) == ""


def test_suggest_improvements_degrades_to_empty(opt):
    # No similar tests available without a knowledge base
    assert opt.suggest_improvements("https://x.com", "obj") == []


def test_get_insights_degraded(opt):
    insights = opt.get_insights("https://github.com/x")
    assert insights["domain"] == "github.com"
    assert insights["similar_tests_count"] == 0
    assert insights["statistics"] == {}
    assert insights["recommendations"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
