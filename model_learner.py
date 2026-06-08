"""
Model Learner - Aprende automáticamente qué modelo es mejor para cada caso
Nivel 5: Máxima dificultad - Learning automático
"""

import json
import time
from typing import Dict, List, Tuple
from pathlib import Path
from model_selector import ModelSelector
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    OllamaLLM = None
from rich.console import Console

console = Console()


class ModelLearner:
    """
    Sistema de learning que optimiza automáticamente qué modelo usar
    basado en resultados históricos de tests.
    
    Aprende:
    - Qué modelo es mejor para qué tipo de página
    - Qué modelo es más rápido
    - Qué modelo tiene mejor tasa de éxito
    
    Uso:
        learner = ModelLearner()
        
        # Durante tests, registra resultados
        learner.record_result(
            url="https://github.com",
            model="mistral",
            task="analysis",
            duration=5.2,
            success=True,
            tokens=450
        )
        
        # Obtén recomendación
        best_model = learner.recommend_model(
            url="https://github.com",
            task="analysis"
        )
    """
    
    LEARNING_FILE = "model_learning.json"
    
    def __init__(self):
        self.learning_data = self._load_learning_data()
    
    def _load_learning_data(self) -> Dict:
        """Carga datos de learning históricos"""
        if Path(self.LEARNING_FILE).exists():
            try:
                with open(self.LEARNING_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self._empty_learning_data()
        return self._empty_learning_data()
    
    def _empty_learning_data(self) -> Dict:
        """Estructura vacía de learning data"""
        return {
            "by_domain": {},
            "by_task": {},
            "by_model": {},
            "total_runs": 0
        }
    
    def _save_learning_data(self) -> None:
        """Guarda datos de learning"""
        with open(self.LEARNING_FILE, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
    
    def record_result(self, url: str, model: str, task: str,
                     duration: float, success: bool, tokens: int = 0) -> None:
        """
        Registra resultado de un test
        
        Args:
            url: URL testeada
            model: Modelo usado
            task: Tipo de tarea ("analysis", "planning", "vision")
            duration: Tiempo en segundos
            success: ¿Fue exitoso?
            tokens: Tokens generados
        """
        # Extrae dominio
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Por dominio
        if domain not in self.learning_data["by_domain"]:
            self.learning_data["by_domain"][domain] = {}
        
        if model not in self.learning_data["by_domain"][domain]:
            self.learning_data["by_domain"][domain][model] = {
                "runs": 0,
                "successes": 0,
                "total_time": 0,
                "total_tokens": 0,
                "tasks": {}
            }
        
        data = self.learning_data["by_domain"][domain][model]
        data["runs"] += 1
        if success:
            data["successes"] += 1
        data["total_time"] += duration
        data["total_tokens"] += tokens
        
        # Por tarea
        if task not in data["tasks"]:
            data["tasks"][task] = {
                "runs": 0,
                "successes": 0,
                "avg_time": 0,
                "avg_tokens": 0
            }
        
        task_data = data["tasks"][task]
        task_data["runs"] += 1
        if success:
            task_data["successes"] += 1
        task_data["avg_time"] = data["total_time"] / data["runs"]
        task_data["avg_tokens"] = data["total_tokens"] / data["runs"]
        
        # Por tarea (global)
        if task not in self.learning_data["by_task"]:
            self.learning_data["by_task"][task] = {}
        
        if model not in self.learning_data["by_task"][task]:
            self.learning_data["by_task"][task][model] = {
                "runs": 0,
                "successes": 0,
                "avg_time": 0,
                "success_rate": 0
            }
        
        task_global = self.learning_data["by_task"][task][model]
        task_global["runs"] += 1
        if success:
            task_global["successes"] += 1
        task_global["success_rate"] = (task_global["successes"] / task_global["runs"]) * 100
        task_global["avg_time"] = duration
        
        # Contador
        self.learning_data["total_runs"] += 1
        
        self._save_learning_data()
    
    def recommend_model(self, url: str = None, task: str = None,
                       optimize: str = "quality") -> str:
        """
        Recomienda mejor modelo basado en learning
        
        Args:
            url: URL a testear (para usar datos de dominio similar)
            task: Tipo de tarea
            optimize: "quality", "speed", o "balanced"
        
        Returns:
            Nombre del modelo recomendado
        """
        candidates = {}
        
        # Si hay dominio, usa datos históricos
        if url:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            if domain in self.learning_data["by_domain"]:
                domain_data = self.learning_data["by_domain"][domain]
                for model, data in domain_data.items():
                    if data["runs"] > 0:
                        success_rate = (data["successes"] / data["runs"]) * 100
                        avg_time = data["total_time"] / data["runs"]
                        
                        candidates[model] = {
                            "success_rate": success_rate,
                            "avg_time": avg_time,
                            "runs": data["runs"]
                        }
        
        # Si no hay datos de dominio, usa datos globales de tarea
        if not candidates and task:
            if task in self.learning_data["by_task"]:
                task_data = self.learning_data["by_task"][task]
                for model, data in task_data.items():
                    if data["runs"] > 0:
                        candidates[model] = {
                            "success_rate": data["success_rate"],
                            "avg_time": data["avg_time"],
                            "runs": data["runs"]
                        }
        
        # Si no hay datos, retorna selector por defecto
        if not candidates:
            selector = ModelSelector(mode="balanced")
            return selector.select(task or "analysis")
        
        # Selecciona según optimize
        if optimize == "quality":
            # Prioriza success rate
            best = max(candidates.items(),
                      key=lambda x: (x[1]["success_rate"], -x[1]["avg_time"]))
        elif optimize == "speed":
            # Prioriza tiempo
            best = min(candidates.items(),
                      key=lambda x: x[1]["avg_time"])
        else:  # balanced
            # Equilibra ambos
            best = max(candidates.items(),
                      key=lambda x: (x[1]["success_rate"], -x[1]["avg_time"]))
        
        return best[0]
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas de learning"""
        return {
            "total_runs": self.learning_data["total_runs"],
            "domains_learned": len(self.learning_data["by_domain"]),
            "tasks_learned": len(self.learning_data["by_task"]),
            "by_domain": self.learning_data["by_domain"],
            "by_task": self.learning_data["by_task"]
        }
    
    def print_stats(self) -> None:
        """Imprime estadísticas bonitas"""
        from rich.table import Table
        
        stats = self.get_stats()
        
        console.print("\n[bold cyan]Learning Statistics[/bold cyan]\n")
        console.print(f"Total runs: {stats['total_runs']}")
        console.print(f"Domains learned: {stats['domains_learned']}")
        console.print(f"Tasks learned: {stats['tasks_learned']}\n")
        
        # Por dominio
        if stats["by_domain"]:
            console.print("[cyan]Mejor modelo por dominio:[/cyan]\n")
            
            table = Table()
            table.add_column("Dominio", style="cyan")
            table.add_column("Mejor Modelo", style="green")
            table.add_column("Success Rate", style="yellow")
            table.add_column("Avg Time", style="magenta")
            
            for domain, models in stats["by_domain"].items():
                best_model = max(models.items(),
                               key=lambda x: x[1]["successes"] / max(x[1]["runs"], 1))
                model_name = best_model[0]
                data = best_model[1]
                success_rate = (data["successes"] / data["runs"]) * 100
                avg_time = data["total_time"] / data["runs"]
                
                table.add_row(
                    domain,
                    model_name,
                    f"{success_rate:.1f}%",
                    f"{avg_time:.2f}s"
                )
            
            console.print(table)
        
        # Por tarea
        if stats["by_task"]:
            console.print("\n[cyan]Mejor modelo por tarea:[/cyan]\n")
            
            table = Table()
            table.add_column("Tarea", style="cyan")
            table.add_column("Mejor Modelo", style="green")
            table.add_column("Success Rate", style="yellow")
            table.add_column("Avg Time", style="magenta")
            
            for task, models in stats["by_task"].items():
                if models:
                    best_model = max(models.items(),
                                   key=lambda x: x[1]["success_rate"])
                    model_name = best_model[0]
                    data = best_model[1]
                    
                    table.add_row(
                        task,
                        model_name,
                        f"{data['success_rate']:.1f}%",
                        f"{data['avg_time']:.2f}s"
                    )
            
            console.print(table)


if __name__ == "__main__":
    print("=== NIVEL 5: Learning Automático ===\n")
    
    learner = ModelLearner()
    
    # Simula algunos resultados
    learner.record_result(
        url="https://github.com",
        model="mistral",
        task="analysis",
        duration=5.2,
        success=True,
        tokens=450
    )
    learner.record_result(
        url="https://github.com",
        model="neural-chat",
        task="analysis",
        duration=3.1,
        success=True,
        tokens=380
    )
    
    # Muestra estadísticas
    learner.print_stats()
    
    # Recomienda modelo
    print("\nModelo recomendado para GitHub (quality):")
    rec = learner.recommend_model(url="https://github.com", task="analysis")
    print(f"  → {rec}")
