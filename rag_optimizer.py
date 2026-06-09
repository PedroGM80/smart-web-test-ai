"""
RAG Optimizer - Mejora planes de testing usando knowledge base
Combina plan inicial con patrones de tests anteriores similares
"""

from typing import List, Dict, Optional
from knowledge_base import TestKnowledgeBase
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    OllamaLLM = None
from rich.console import Console

console = Console()


class RAGOptimizer:
    """
    Optimizador de planes usando RAG
    
    Busca tests anteriores similares y usa sus mejores prácticas
    para mejorar el plan de testing del test actual.
    
    Workflow:
    1. Recibe plan inicial generado por IA
    2. Busca tests similares en knowledge base
    3. Extrae patrones de tests exitosos
    4. IA mejora el plan combinando ambos
    5. Retorna plan optimizado
    
    Example:
        optimizer = RAGOptimizer()
        initial_plan = "Cargar página → verificar elementos"
        improved = optimizer.improve_plan(
            url="https://example.com",
            initial_plan=initial_plan,
            objectives="Testear página"
        )
    """
    
    def __init__(self, 
                 knowledge_base: Optional[TestKnowledgeBase] = None,
                 llm_model: str = "mistral",
                 embedding_model: str = "mistral"):
        """
        Inicializa optimizer
        
        Args:
            knowledge_base: Instancia de TestKnowledgeBase (crea una si no proporciona)
            llm_model: Modelo para LLM
            embedding_model: Modelo para embeddings
        """
        
        self.kb = knowledge_base or TestKnowledgeBase(embedding_model=embedding_model)
        self.llm = OllamaLLM(model=llm_model) if OllamaLLM else None
        self.embedding_model = embedding_model
    
    def improve_plan(self,
                    url: str,
                    initial_plan: str,
                    objectives: str,
                    use_similar: bool = True) -> str:
        """
        Mejora plan inicial usando RAG
        
        Args:
            url: URL a testear
            initial_plan: Plan inicial generado por IA
            objectives: Objetivos del test
            use_similar: Usar tests similares (True = RAG, False = solo LLM)
        
        Returns:
            Plan optimizado
        """
        
        console.print("[cyan]Optimizando plan con RAG...[/cyan]")
        
        if not use_similar:
            return initial_plan
        
        # Busca tests similares
        similar_tests = self.kb.find_similar_tests(
            url=url,
            objectives=objectives,
            k=3,
            min_pass_rate=85.0  # Solo tests con buen pass rate
        )
        
        if not similar_tests:
            console.print("[yellow]⚠ No hay tests similares, usando plan inicial[/yellow]")
            return initial_plan
        
        # Extrae patrones de tests similares
        patterns = self._extract_patterns(similar_tests)
        
        # IA mejora el plan
        improved_plan = self._optimize_with_llm(
            initial_plan=initial_plan,
            patterns=patterns,
            objectives=objectives
        )
        
        return improved_plan
    
    def _extract_patterns(self, similar_tests: List[Dict]) -> str:
        """
        Extrae patrones de tests similares exitosos
        
        Args:
            similar_tests: Lista de tests similares
        
        Returns:
            String con patrones extraídos
        """
        
        patterns = "PATRONES DE TESTS SIMILARES EXITOSOS:\n"
        patterns += "=" * 50 + "\n"
        
        for i, test in enumerate(similar_tests, 1):
            patterns += f"\nTest {i}: {test['url']}\n"
            patterns += f"Pass Rate: {test['pass_rate']:.1f}%\n"
            patterns += f"Plan:\n{test['document']}\n"
            patterns += "-" * 50 + "\n"
        
        return patterns
    
    def _optimize_with_llm(self,
                          initial_plan: str,
                          patterns: str,
                          objectives: str) -> str:
        """
        Usa LLM para mejorar plan combinando con patrones
        
        Args:
            initial_plan: Plan inicial
            patterns: Patrones de tests similares
            objectives: Objetivos del test
        
        Returns:
            Plan mejorado
        """
        
        prompt = f"""
Eres un QA expert. Tu tarea es mejorar un plan de testing combinando:
1. El plan inicial generado automáticamente
2. Patrones de tests anteriores similares que fueron exitosos

PLAN INICIAL:
{initial_plan}

{patterns}

OBJETIVO DEL TEST:
{objectives}

TAREA:
1. Analiza el plan inicial
2. Compara con patrones exitosos anteriores
3. Incorpora las mejores prácticas de tests similares
4. Mejora el plan manteniendo la estructura original
5. Agrega validaciones que faltaban
6. Optimiza el orden de pasos

Retorna solo el plan mejorado, sin explicaciones adicionales.
Mantén el formato original pero mejorado.
"""
        
        improved = self.llm.invoke(prompt)
        console.print("[green]✓ Plan optimizado con patrones anteriores[/green]")
        
        return improved
    
    def suggest_improvements(self, 
                            url: str,
                            objectives: str) -> List[str]:
        """
        Sugiere mejoras para un test basado en experiencia anterior
        
        Args:
            url: URL a testear
            objectives: Objetivos del test
        
        Returns:
            Lista de sugerencias
        """
        
        # Busca tests similares
        similar_tests = self.kb.find_similar_tests(
            url=url,
            objectives=objectives,
            k=5
        )
        
        if not similar_tests:
            return []
        
        # Obtén estadísticas del dominio
        domain = self._extract_domain(url)
        stats = self.kb.get_domain_statistics(domain)
        
        suggestions = []
        
        # Basado en estadísticas
        if stats.get("avg_pass_rate", 0) < 70:
            suggestions.append(
                "⚠ Este dominio históricamente tiene baja tasa de éxito. "
                "Considera más validaciones."
            )
        
        # Basado en tests anteriores
        if similar_tests:
            best_test = max(similar_tests, key=lambda x: x["pass_rate"])
            suggestions.append(
                f"✓ Test similar exitoso encontrado con {best_test['pass_rate']:.1f}% pass rate. "
                f"Usar como referencia."
            )
        
        # Basado en patrones
        if len(similar_tests) > 2:
            common_patterns = self._find_common_patterns(similar_tests)
            if common_patterns:
                suggestions.append(
                    f"📊 Patrones comunes encontrados: {common_patterns}"
                )
        
        return suggestions
    
    def _find_common_patterns(self, tests: List[Dict]) -> str:
        """Encuentra patrones comunes en múltiples tests"""
        # Análisis simple de patrones
        keywords = []
        for test in tests:
            doc = test.get("document", "")
            if "formulario" in doc.lower():
                keywords.append("formulario")
            if "botón" in doc.lower():
                keywords.append("botones")
            if "búsqueda" in doc.lower():
                keywords.append("búsqueda")
        
        if keywords:
            return ", ".join(set(keywords))
        return ""
    
    def _extract_domain(self, url: str) -> str:
        """Extrae dominio de URL"""
        try:
            return url.replace("https://", "").replace("http://", "").split("/")[0]
        except:
            return "unknown"
    
    def get_insights(self, url: str) -> Dict:
        """
        Obtiene insights sobre testing histórico de una URL
        
        Args:
            url: URL a analizar
        
        Returns:
            Dict con insights
        """
        
        domain = self._extract_domain(url)
        stats = self.kb.get_domain_statistics(domain)
        similar = self.kb.find_similar_tests(url=url, objectives="", k=5)
        
        return {
            "domain": domain,
            "statistics": stats,
            "similar_tests_count": len(similar),
            "recommendations": self.suggest_improvements(url, "")
        }


def create_rag_optimizer(knowledge_base: Optional[TestKnowledgeBase] = None) -> RAGOptimizer:
    """
    Factory function para crear RAGOptimizer
    
    Args:
        knowledge_base: Knowledge base existente (opcional)
    
    Returns:
        Instancia de RAGOptimizer
    """
    return RAGOptimizer(knowledge_base=knowledge_base)


if __name__ == "__main__":
    # Ejemplo de uso
    optimizer = RAGOptimizer()
    
    initial_plan = """
    1. Cargar página
    2. Esperar a que cargue
    3. Verificar título
    """
    
    improved = optimizer.improve_plan(
        url="https://example.com",
        initial_plan=initial_plan,
        objectives="Testear página de ejemplo"
    )
    
    print("PLAN MEJORADO:")
    print(improved)
    
    # Sugerencias
    suggestions = optimizer.suggest_improvements(
        url="https://example.com",
        objectives="Testear"
    )
    
    if suggestions:
        print("\nSUGERENCIAS:")
        for sugg in suggestions:
            print(f"  • {sugg}")
