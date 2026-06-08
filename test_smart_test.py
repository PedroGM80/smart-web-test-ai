"""
Tests para Smart Test
Pytest suite
"""

import pytest
from model_selector import ModelSelector
from pathlib import Path


class TestModelSelector:
    """Tests para Model Selector"""
    
    def test_selector_init(self):
        """Test inicialización"""
        selector = ModelSelector(mode="balanced")
        assert selector.mode == "balanced"
    
    def test_selector_select(self):
        """Test selección de modelo"""
        selector = ModelSelector(mode="speed")
        model = selector.select("analysis")
        assert model == "neural-chat"
    
    def test_selector_modes(self):
        """Test todos los modos"""
        for mode in ["speed", "balanced", "quality"]:
            selector = ModelSelector(mode=mode)
            assert selector.mode == mode
            assert selector.select("analysis") is not None
    
    def test_selector_set_model(self):
        """Test set modelo personalizado"""
        selector = ModelSelector()
        selector.set_model("analysis", "mistral")
        assert selector.select("analysis") == "mistral"
    
    def test_selector_get_llm(self):
        """Test get LLM (sin iniciar Ollama)"""
        selector = ModelSelector()
        # No ejecuta, solo verifica que la función existe
        assert hasattr(selector, 'get_llm')


class TestFiles:
    """Tests para archivos y estructura"""
    
    def test_main_files_exist(self):
        """Verifica que existen archivos principales"""
        required_files = [
            "smart_test.py",
            "agent.py",
            "model_selector.py",
            "advanced_rag.py",
            "smart_test_ui.py",
            "requirements.txt",
            "README.md"
        ]
        
        for file in required_files:
            assert Path(file).exists(), f"Missing: {file}"
    
    def test_docs_exist(self):
        """Verifica documentación"""
        docs = [
            "README.md",
            "MODEL_SELECTOR.md",
            "WEB_UI.md",
            "RAG.md",
            "CUCUMBER.md",
            "GRAFANA.md"
        ]
        
        for doc in docs:
            assert Path(doc).exists(), f"Missing doc: {doc}"
    
    def test_requirements_installed(self):
        """Verifica que requirements.txt es válido"""
        req_file = Path("requirements.txt")
        assert req_file.exists()
        
        content = req_file.read_text()
        assert "playwright" in content
        assert "ollama" in content
        assert "streamlit" in content


class TestImports:
    """Tests de imports"""
    
    def test_import_model_selector(self):
        """Test import model_selector"""
        try:
            from model_selector import ModelSelector
            assert ModelSelector is not None
        except ImportError:
            pytest.skip("Requires model_selector module")
    
    def test_import_agent(self):
        """Test import agent"""
        try:
            from agent import SmartTestAgent
            assert SmartTestAgent is not None
        except ImportError:
            pytest.skip("Requires agent module")


class TestPersistReport:
    """persist_report stores a run through the repository"""

    def _repo(self):
        from database import Base, create_db_engine, create_session_factory
        from repositories import TestRepository
        engine = create_db_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        return TestRepository(create_session_factory(engine))

    def test_persist_writes_to_repository(self):
        from smart_test import persist_report
        repo = self._repo()
        report = {"pass_rate": 88.0, "duration": 15.0, "status": "success"}
        persist_report(repo, url="https://x.com", objective="o", model="mistral", report=report)

        stored = repo.list_chronological()
        assert len(stored) == 1
        assert stored[0].url == "https://x.com"
        assert stored[0].pass_rate == 88.0

    def test_persist_handles_missing_fields(self):
        from smart_test import persist_report
        repo = self._repo()
        persist_report(repo, url="https://y.com", objective="o", model="mistral", report={})
        stored = repo.list_chronological()
        assert len(stored) == 1
        assert stored[0].pass_rate == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
