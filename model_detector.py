"""
Model Detector - Auto-detección de modelos Ollama disponibles
Nivel 3: Avanzado - Auto-detection y descarga
"""

import subprocess
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from model_selector import ModelSelector

console = Console()


class ModelDetector:
    """
    Detecta modelos disponibles y sugiere configuración óptima
    
    Uso:
        detector = ModelDetector()
        available = detector.get_available_models()
        suggestion = detector.suggest_optimal_config()
    """
    
    def __init__(self):
        self.available_models = self._detect_models()
    
    def _detect_models(self) -> List[str]:
        """Detecta qué modelos están descargados en Ollama"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                console.print("[yellow]⚠ Ollama no está ejecutándose[/yellow]")
                return []
            
            # Parse output
            models = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            
            return models
        
        except FileNotFoundError:
            console.print("[yellow]⚠ Ollama no encontrado en PATH[/yellow]")
            return []
        except subprocess.TimeoutExpired:
            console.print("[yellow]⚠ Timeout detectando modelos[/yellow]")
            return []
        except Exception as e:
            console.print(f"[yellow]⚠ Error detectando modelos: {e}[/yellow]")
            return []
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos disponibles"""
        return self.available_models
    
    def has_model(self, model_name: str) -> bool:
        """Verifica si un modelo está disponible"""
        return any(model_name in model for model in self.available_models)
    
    def suggest_optimal_config(self) -> Dict[str, str]:
        """
        Sugiere configuración óptima basada en modelos disponibles
        
        Returns:
            Dict con asignación óptima de modelos por tarea
        """
        config = {
            "analysis": "neural-chat",
            "planning": "mistral",
            "vision": "llava"
        }
        
        # Ajusta según disponibilidad
        
        # Analysis
        if self.has_model("neural-chat"):
            config["analysis"] = "neural-chat"
        elif self.has_model("mistral"):
            config["analysis"] = "mistral"
        elif self.has_model("orca"):
            config["analysis"] = "orca-mini"
        
        # Planning
        if self.has_model("mistral"):
            config["planning"] = "mistral"
        elif self.has_model("dolphin"):
            config["planning"] = "dolphin-mixtral"
        elif self.has_model("neural-chat"):
            config["planning"] = "neural-chat"
        
        # Vision
        if self.has_model("llava"):
            config["vision"] = "llava"
        elif self.has_model("llava-phi"):
            config["vision"] = "llava-phi"
        
        return config
    
    def download_missing_models(self, models_to_use: List[str]) -> bool:
        """
        Descarga modelos faltantes automáticamente
        
        Args:
            models_to_use: Lista de modelos necesarios
        
        Returns:
            True si descargó algo, False si todo está OK
        """
        missing = [m for m in models_to_use if not self.has_model(m)]
        
        if not missing:
            console.print("[green]✓ Todos los modelos están disponibles[/green]")
            return False
        
        console.print(f"\n[yellow]Modelos faltantes: {', '.join(missing)}[/yellow]")
        console.print("[yellow]¿Descargar automáticamente?[/yellow]\n")
        
        for model in missing:
            console.print(f"[cyan]Descargando {model}...[/cyan]")
            try:
                subprocess.run(
                    ["ollama", "pull", model],
                    timeout=600,  # 10 min timeout
                    check=True
                )
                console.print(f"[green]✓ {model} descargado[/green]")
            except subprocess.CalledProcessError:
                console.print(f"[red]✗ Error descargando {model}[/red]")
            except subprocess.TimeoutExpired:
                console.print(f"[red]✗ Timeout descargando {model}[/red]")
        
        return True
    
    def print_status(self) -> None:
        """Imprime estado de modelos"""
        from rich.table import Table
        
        if not self.available_models:
            console.print("[red]✗ No hay modelos Ollama disponibles[/red]")
            console.print("[yellow]Ejecuta: ollama pull mistral[/yellow]")
            return
        
        console.print(f"\n[green]✓ Modelos disponibles ({len(self.available_models)}):[/green]\n")
        
        table = Table()
        table.add_column("Modelo", style="cyan")
        table.add_column("Disponible", style="green")
        
        # Todos los modelos conocidos
        all_models = set(ModelSelector.MODELS_INFO.keys())
        all_models.update(self.available_models)
        
        for model in sorted(all_models):
            available = "✓" if self.has_model(model) else "✗"
            table.add_row(model, available)
        
        console.print(table)
    
    def suggest_setup(self) -> None:
        """Sugiere setup óptimo basado en lo disponible"""
        self.print_status()
        
        config = self.suggest_optimal_config()
        
        console.print(f"\n[cyan]Configuración sugerida:[/cyan]\n")
        
        table = Table()
        table.add_column("Tarea", style="cyan")
        table.add_column("Modelo", style="green")
        
        for task, model in config.items():
            table.add_row(task, model)
        
        console.print(table)
        
        console.print(f"\n[yellow]Usa:[/yellow]")
        console.print(f"  python smart_test.py ... --optimize balanced")


if __name__ == "__main__":
    print("=== NIVEL 3: Auto-Detection ===\n")
    
    detector = ModelDetector()
    detector.suggest_setup()
