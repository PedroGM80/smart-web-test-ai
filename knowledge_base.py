"""
Knowledge Base - RAG para Smart Web Test
Almacena y aprende de tests anteriores usando ChromaDB + embeddings locales
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# ChromaDB + Ollama embeddings are only needed for the live knowledge base.
# Import defensively so the module loads (and degrades to a no-op) without them.
try:
    from chromadb.config import Settings
    import chromadb
except ImportError:
    chromadb = None
    Settings = None
try:
    from langchain_community.embeddings import OllamaEmbeddings
except ImportError:
    OllamaEmbeddings = None
from rich.console import Console

console = Console()


class TestKnowledgeBase:
    """
    Knowledge Base para Smart Web Test
    
    Almacena tests anteriores y aprende de ellos para mejorar tests futuros.
    Usa ChromaDB como vector database y OllamaEmbeddings para embeddings locales.
    
    Features:
    - Guardar tests completados
    - Buscar tests similares
    - Patrones de testing reutilizables
    - Mejora automática con experiencia
    
    Example:
        kb = TestKnowledgeBase()
        
        # Guardar test
        kb.store_test(
            url="https://github.com/langchain-ai/deepagents",
            objectives="Testear repo",
            plan="Plan de testing",
            results={"pass_rate": 95}
        )
        
        # Buscar similares
        similar = kb.find_similar_tests(
            url="https://github.com/facebook/react",
            objectives="Testear repo"
        )
    """
    
    __test__ = False  # avoid pytest collection (class name starts with Test)
    
    def __init__(self, 
                 knowledge_dir: str = "./knowledge",
                 embedding_model: str = "mistral",
                 collection_name: str = "test_patterns"):
        """
        Inicializa Knowledge Base
        
        Args:
            knowledge_dir: Directorio para almacenar ChromaDB
            embedding_model: Modelo Ollama para embeddings
            collection_name: Nombre de colección en ChromaDB
        """
        
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        
        # Inicializa ChromaDB
        try:
            self.embeddings = OllamaEmbeddings(model=embedding_model)
            
            # Configuración de ChromaDB
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.knowledge_dir),
                anonymized_telemetry=False
            )
            
            self.client = chromadb.Client(settings)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            console.print("[green]✓ Knowledge Base inicializado[/green]")
            self._log_stats()
        
        except Exception as e:
            console.print(f"[red]Error inicializando Knowledge Base: {e}[/red]")
            console.print("[yellow]  Verifica que Ollama está corriendo[/yellow]")
            self.collection = None
    
    def store_test(self, 
                   url: str,
                   objectives: str,
                   plan: str,
                   results: Dict,
                   cucumber_features: Optional[str] = None) -> bool:
        """
        Guarda un test completado en la knowledge base
        
        Args:
            url: URL testeada
            objectives: Objetivos del test
            plan: Plan de testing generado
            results: Resultados del test (dict con métricas)
            cucumber_features: Feature file generado (opcional)
        
        Returns:
            True si fue exitoso
        """
        
        if not self.collection:
            console.print("[yellow]Knowledge Base no disponible[/yellow]")
            return False
        
        try:
            # Crea documento con contexto de test
            doc = self._create_test_document(
                url=url,
                objectives=objectives,
                plan=plan,
                results=results,
                features=cucumber_features
            )
            
            # Metadata para filtrado
            metadata = {
                "url": url,
                "domain": self._extract_domain(url),
                "objectives_keywords": " ".join(objectives.split()[:5]),
                "pass_rate": float(results.get("pass_rate", 0)),
                "timestamp": datetime.now().isoformat(),
                "success": results.get("failed_actions", 0) == 0
            }
            
            # Genera ID único
            doc_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(url) % 10000}"
            
            # Almacena en ChromaDB
            self.collection.add(
                ids=[doc_id],
                documents=[doc],
                metadatas=[metadata]
            )
            
            console.print(f"[green]✓ Test guardado en knowledge base[/green]")
            console.print(f"  ID: {doc_id}")
            console.print(f"  URL: {url}")
            console.print(f"  Pass Rate: {results.get('pass_rate', 0):.1f}%")
            
            return True
        
        except Exception as e:
            console.print(f"[red]Error guardando test: {e}[/red]")
            return False
    
    def find_similar_tests(self, 
                          url: str,
                          objectives: str,
                          k: int = 3,
                          min_pass_rate: float = 80.0) -> List[Dict]:
        """
        Busca tests similares en la knowledge base
        
        Args:
            url: URL a testear
            objectives: Objetivos del test
            k: Número de resultados
            min_pass_rate: Filtro: solo tests con pass_rate >= este valor
        
        Returns:
            Lista de tests similares
        """
        
        if not self.collection:
            return []
        
        try:
            # Crea query
            query = f"Testing {self._extract_domain(url)} - {objectives}"
            
            # Busca en ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=k * 2,  # Busca más para filtrar
                where={"pass_rate": {"$gte": min_pass_rate}} if min_pass_rate > 0 else None
            )
            
            # Procesa resultados
            similar_tests = []
            
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0][:k]):
                    metadata = results["metadatas"][0][i]
                    
                    similar_tests.append({
                        "document": doc,
                        "url": metadata.get("url"),
                        "pass_rate": metadata.get("pass_rate"),
                        "timestamp": metadata.get("timestamp"),
                        "success": metadata.get("success")
                    })
            
            if similar_tests:
                console.print(f"[cyan]Encontrados {len(similar_tests)} tests similares[/cyan]")
                for test in similar_tests:
                    console.print(f"  • {test['url']} (Pass Rate: {test['pass_rate']:.1f}%)")
            
            return similar_tests
        
        except Exception as e:
            console.print(f"[yellow]Error buscando tests similares: {e}[/yellow]")
            return []
    
    def get_domain_statistics(self, domain: str) -> Dict:
        """
        Obtiene estadísticas de tests para un dominio
        
        Args:
            domain: Dominio (ej: "github.com")
        
        Returns:
            Dict con estadísticas
        """
        
        if not self.collection:
            return {}
        
        try:
            results = self.collection.get(
                where={"domain": domain}
            )
            
            if not results or not results["ids"]:
                return {}
            
            pass_rates = [m.get("pass_rate", 0) for m in results["metadatas"]]
            successes = sum(1 for m in results["metadatas"] if m.get("success"))
            
            return {
                "domain": domain,
                "total_tests": len(results["ids"]),
                "successful_tests": successes,
                "avg_pass_rate": sum(pass_rates) / len(pass_rates) if pass_rates else 0,
                "best_pass_rate": max(pass_rates) if pass_rates else 0,
                "worst_pass_rate": min(pass_rates) if pass_rates else 0
            }
        
        except Exception as e:
            console.print(f"[yellow]Error obteniendo estadísticas: {e}[/yellow]")
            return {}
    
    def export_knowledge(self, export_path: str = "knowledge_export.json") -> bool:
        """
        Exporta knowledge base a JSON
        
        Args:
            export_path: Ruta para exportar
        
        Returns:
            True si fue exitoso
        """
        
        if not self.collection:
            return False
        
        try:
            results = self.collection.get()
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_tests": len(results["ids"]),
                "tests": []
            }
            
            for i, doc_id in enumerate(results["ids"]):
                export_data["tests"].append({
                    "id": doc_id,
                    "document": results["documents"][i] if results["documents"] else "",
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            console.print(f"[green]✓ Knowledge base exportado a {export_path}[/green]")
            return True
        
        except Exception as e:
            console.print(f"[red]Error exportando: {e}[/red]")
            return False
    
    def _create_test_document(self, 
                             url: str,
                             objectives: str,
                             plan: str,
                             results: Dict,
                             features: Optional[str] = None) -> str:
        """Crea documento de test para embedding"""
        
        doc = f"""
TEST REPORT
===========

URL: {url}
Objectives: {objectives}

PLAN:
{plan}

RESULTS:
- Total Actions: {results.get('total_actions', 0)}
- Passed Actions: {results.get('passed_actions', 0)}
- Failed Actions: {results.get('failed_actions', 0)}
- Pass Rate: {results.get('pass_rate', 0):.1f}%
- Validation: {results.get('validation', 'Unknown')}
"""
        
        if features:
            doc += f"\nFEATURES:\n{features}"
        
        return doc.strip()
    
    def _extract_domain(self, url: str) -> str:
        """Extrae dominio de URL"""
        try:
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
            return domain
        except:
            return "unknown"
    
    def _log_stats(self):
        """Registra estadísticas de la knowledge base"""
        try:
            if self.collection:
                count = self.collection.count()
                console.print(f"[dim]Knowledge Base: {count} tests almacenados[/dim]")
        except:
            pass


def create_knowledge_base(embedding_model: str = "mistral") -> Optional[TestKnowledgeBase]:
    """
    Factory function para crear Knowledge Base
    
    Args:
        embedding_model: Modelo Ollama a usar
    
    Returns:
        Instancia de TestKnowledgeBase o None si falla
    """
    
    try:
        return TestKnowledgeBase(embedding_model=embedding_model)
    except Exception as e:
        console.print(f"[red]Error creando Knowledge Base: {e}[/red]")
        return None


if __name__ == "__main__":
    # Ejemplo de uso
    kb = TestKnowledgeBase()
    
    # Guarda un test
    kb.store_test(
        url="https://example.com",
        objectives="Testear página de ejemplo",
        plan="1. Cargar página\n2. Verificar elementos\n3. Validar contenido",
        results={
            "total_actions": 10,
            "passed_actions": 10,
            "failed_actions": 0,
            "pass_rate": 100.0
        }
    )
    
    # Busca similares
    similar = kb.find_similar_tests(
        url="https://example.com/page2",
        objectives="Testear página"
    )
    
    # Estadísticas
    stats = kb.get_domain_statistics("example.com")
    print(f"\nEstadísticas: {stats}")
