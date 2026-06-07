"""
Model Benchmarker - Compara modelos por velocidad y calidad
Nivel 4: Experto - Benchmarking automático
"""

import time
import json
from typing import Dict, List
from langchain_ollama import OllamaLLM
from model_detector import ModelDetector
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()


class ModelBenchmarker:
    """
    Benchmarkea modelos locales por velocidad y calidad
    
    Uso:
        benchmarker = ModelBenchmarker()
        results = benchmarker.benchmark_models(["mistral", "neural-chat"])
        benchmarker.show_results()
        benchmarker.recommend()
    """
    
    # Tests de evaluación
    BENCHMARK_TESTS = {
        "analysis": {
            "prompt": "Analiza esta estructura HTML y extrae: título, enlaces principales, formularios. <html><head><title>Test Page</title></head><body><h1>Welcome</h1><a href='#'>Link</a><form><input/></form></body></html>",
            "timeout": 15,
            "description": "Análisis HTML"
        },
        "planning": {
            "prompt": "Crea un plan de testing para una página de login con campos email y password. El plan debe tener 5 pasos.",
            "timeout": 20,
            "description": "Generación de plan"
        },
        "reasoning": {
            "prompt": "Si una página tarda 2 segundos en cargar y hacemos 100 clicks, ¿cuánto tiempo total? Explica el razonamiento.",
            "timeout": 15,
            "description": "Razonamiento"
        }
    }
    
    def __init__(self):
        self.detector = ModelDetector()
        self.results = {}
    
    def benchmark_model(self, model_name: str) -> Dict:
        """
        Benchmarkea un modelo individual
        
        Returns:
            Dict con métricas: velocidad, tokens/s, etc
        """
        console.print(f"\n[cyan]Benchmarkeando {model_name}...[/cyan]")
        
        llm = OllamaLLM(model=model_name)
        model_results = {
            "model": model_name,
            "tests": {}
        }
        
        for test_name, test_data in track(
            self.BENCHMARK_TESTS.items(),
            description=f"Ejecutando tests..."
        ):
            try:
                # Mide tiempo
                start = time.time()
                response = llm.invoke(test_data["prompt"], timeout=test_data["timeout"])
                elapsed = time.time() - start
                
                tokens = len(response.split()) if response else 0
                tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
                
                model_results["tests"][test_name] = {
                    "time_seconds": round(elapsed, 2),
                    "tokens": tokens,
                    "tokens_per_second": round(tokens_per_sec, 1),
                    "response_length": len(response),
                    "status": "✓"
                }
            
            except Exception as e:
                model_results["tests"][test_name] = {
                    "status": "✗",
                    "error": str(e)
                }
        
        return model_results
    
    def benchmark_models(self, models: List[str] = None) -> Dict:
        """
        Benchmarkea múltiples modelos
        
        Args:
            models: Lista de modelos. Si es None, benchmarkea los disponibles
        
        Returns:
            Dict con resultados de todos
        """
        if models is None:
            models = self.detector.get_available_models()
        
        if not models:
            console.print("[red]No hay modelos disponibles[/red]")
            return {}
        
        console.print(f"\n[bold cyan]Benchmarking {len(models)} modelos...[/bold cyan]")
        
        self.results = {}
        for model in models:
            self.results[model] = self.benchmark_model(model)
        
        return self.results
    
    def show_results(self) -> None:
        """Muestra resultados en tabla bonita"""
        if not self.results:
            console.print("[yellow]Sin resultados. Ejecuta benchmark_models() primero[/yellow]")
            return
        
        # Tabla general
        console.print("\n[bold cyan]Resultados de Benchmarking[/bold cyan]\n")
        
        for model, data in self.results.items():
            console.print(f"\n[green]{model}[/green]")
            
            table = Table(show_header=True)
            table.add_column("Test", style="cyan")
            table.add_column("Tiempo (s)", justify="right")
            table.add_column("Tokens", justify="right")
            table.add_column("Tokens/s", justify="right")
            table.add_column("Status")
            
            for test_name, test_data in data.get("tests", {}).items():
                if test_data.get("status") == "✓":
                    table.add_row(
                        test_name,
                        f"{test_data['time_seconds']}",
                        f"{test_data['tokens']}",
                        f"{test_data['tokens_per_second']}",
                        "[green]✓[/green]"
                    )
                else:
                    table.add_row(
                        test_name,
                        "-",
                        "-",
                        "-",
                        f"[red]✗ {test_data.get('error', 'Error')}[/red]"
                    )
            
            console.print(table)
    
    def compare(self) -> None:
        """Compara modelos lado a lado"""
        if not self.results:
            console.print("[yellow]Sin resultados[/yellow]")
            return
        
        console.print("\n[bold cyan]Comparativa de Modelos[/bold cyan]\n")
        
        # Por test
        for test_name in self.BENCHMARK_TESTS.keys():
            console.print(f"\n[cyan]{test_name}:[/cyan]")
            
            table = Table()
            table.add_column("Modelo", style="cyan")
            table.add_column("Tiempo (s)", justify="right", style="green")
            table.add_column("Tokens/s", justify="right", style="yellow")
            
            times = []
            for model, data in self.results.items():
                test_data = data.get("tests", {}).get(test_name)
                if test_data and test_data.get("status") == "✓":
                    time_val = test_data["time_seconds"]
                    tokens_per_sec = test_data["tokens_per_second"]
                    times.append((model, time_val, tokens_per_sec))
            
            # Ordena por tiempo
            for model, time_val, tokens_per_sec in sorted(times, key=lambda x: x[1]):
                table.add_row(model, str(time_val), str(tokens_per_sec))
            
            console.print(table)
    
    def recommend(self) -> None:
        """Recomienda mejor modelo por caso de uso"""
        if not self.results:
            console.print("[yellow]Sin resultados[/yellow]")
            return
        
        console.print("\n[bold cyan]Recomendaciones[/bold cyan]\n")
        
        # Modelos exitosos
        successful = {
            model: data for model, data in self.results.items()
            if all(t.get("status") == "✓" for t in data.get("tests", {}).values())
        }
        
        if not successful:
            console.print("[yellow]Ningún modelo completó todos los tests[/yellow]")
            return
        
        # Por uso
        console.print("[cyan]Para Velocidad (tokens/s):[/cyan]")
        fastest = max(
            successful.items(),
            key=lambda x: sum(
                t.get("tokens_per_second", 0)
                for t in x[1].get("tests", {}).values()
            )
        )
        console.print(f"  ➤ {fastest[0]}")
        
        console.print("\n[cyan]Para Análisis:[/cyan]")
        analysis_best = max(
            successful.items(),
            key=lambda x: x[1].get("tests", {}).get("analysis", {}).get("tokens", 0)
        )
        console.print(f"  ➤ {analysis_best[0]}")
        
        console.print("\n[cyan]Para Planning:[/cyan]")
        planning_best = max(
            successful.items(),
            key=lambda x: x[1].get("tests", {}).get("planning", {}).get("tokens", 0)
        )
        console.print(f"  ➤ {planning_best[0]}")
        
        console.print("\n[cyan]Para Razonamiento:[/cyan]")
        reasoning_best = max(
            successful.items(),
            key=lambda x: x[1].get("tests", {}).get("reasoning", {}).get("tokens", 0)
        )
        console.print(f"  ➤ {reasoning_best[0]}")
    
    def save_results(self, filename: str = "benchmark_results.json") -> None:
        """Guarda resultados en JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        console.print(f"\n[green]✓ Resultados guardados en {filename}[/green]")
    
    def load_results(self, filename: str = "benchmark_results.json") -> None:
        """Carga resultados desde JSON"""
        try:
            with open(filename, 'r') as f:
                self.results = json.load(f)
            console.print(f"[green]✓ Resultados cargados desde {filename}[/green]")
        except FileNotFoundError:
            console.print(f"[red]✗ Archivo no encontrado: {filename}[/red]")


if __name__ == "__main__":
    print("=== NIVEL 4: Benchmarking ===\n")
    
    benchmarker = ModelBenchmarker()
    benchmarker.benchmark_models()
    benchmarker.show_results()
    benchmarker.compare()
    benchmarker.recommend()
    benchmarker.save_results()
