"""
Tests de ejemplo usando SmartTestAgent
Ejecutar: pytest test_examples.py -v
"""

import pytest
from agent import SmartTestAgent


class TestSmartAgent:
    """Tests de SmartTestAgent"""
    
    @pytest.fixture
    def agent(self):
        """Inicializa agente para cada test"""
        return SmartTestAgent()
    
    def test_github_deepagents(self, agent):
        """Test: GitHub - deepagents repo"""
        report = agent.test_web(
            url="https://github.com/langchain-ai/deepagents",
            objectives="Verificar que el repositorio carga correctamente y analizar estructura"
        )
        
        assert report is not None
        assert report['url'] == "https://github.com/langchain-ai/deepagents"
        assert report['execution']['passed'] > 0
    
    def test_wikipedia_search(self, agent):
        """Test: Wikipedia - buscar y validar"""
        report = agent.test_web(
            url="https://www.wikipedia.org",
            objectives="Cargar página principal y analizar estructura de búsqueda"
        )
        
        assert report is not None
        assert "execution" in report
        assert report['execution']['total'] > 0
    
    def test_simple_page_load(self, agent):
        """Test simple: carga de página"""
        report = agent.test_web(
            url="https://example.com",
            objectives="Verificar carga básica de página"
        )
        
        assert report is not None
        assert report['execution']['failed'] == 0


class TestAgentComponents:
    """Tests de componentes individuales"""
    
    def test_agent_initialization(self):
        """Verifica inicialización del agente"""
        agent = SmartTestAgent(model="mistral", vision_model="llava")
        
        assert agent.model == "mistral"
        assert agent.vision_model == "llava"
        assert agent.screenshots_dir.exists()
        assert agent.reports_dir.exists()
    
    def test_screenshot_dir_creation(self):
        """Verifica creación de directorios"""
        agent = SmartTestAgent()
        
        assert agent.screenshots_dir.is_dir()
        assert agent.reports_dir.is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
