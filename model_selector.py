"""
Model Selector - Selecciona modelos locales por tarea
Nivel 1: Básico - Selector simple
"""

from typing import Optional, Dict
from langchain_ollama import OllamaLLM


class ModelSelector:
    """
    Selector básico de modelos Ollama por tarea
    
    Uso:
        selector = ModelSelector(mode="balanced")
        model = selector.select("planning")
        
        # O manual
        selector = ModelSelector()
        selector.set_model("planning", "mistral")
        selector.set_model("analysis", "neural-chat")
    """
    
    # Configuraciones predefinidas
    PRESETS = {
        "speed": {
            "analysis": "neural-chat",
            "planning": "orca-mini",
            "vision": "llava-phi"
        },
        "balanced": {
            "analysis": "neural-chat",
            "planning": "mistral",
            "vision": "llava"
        },
        "quality": {
            "analysis": "mistral",
            "planning": "mistral",
            "vision": "llava"
        }
    }
    
    # Modelos disponibles y características
    MODELS_INFO = {
        "orca-mini": {"size": "3B", "speed": "⚡⚡⚡", "quality": "⭐⭐"},
        "neural-chat": {"size": "7B", "speed": "⚡⚡", "quality": "⭐⭐⭐"},
        "mistral": {"size": "7B", "speed": "⚡⚡", "quality": "⭐⭐⭐⭐"},
        "dolphin-mixtral": {"size": "8x7B", "speed": "⚡", "quality": "⭐⭐⭐⭐⭐"},
        "llava": {"size": "7B", "speed": "⚡⚡", "quality": "⭐⭐⭐"},
        "llava-phi": {"size": "3B", "speed": "⚡⚡⚡", "quality": "⭐⭐"}
    }
    
    def __init__(self, mode: str = "balanced"):
        """
        Inicializa con preset
        
        Args:
            mode: "speed", "balanced", o "quality"
        """
        self.mode = mode
        self.config = self.PRESETS.get(mode, self.PRESETS["balanced"]).copy()
        self.llms = {}
    
    def select(self, task: str) -> str:
        """
        Selecciona modelo para una tarea
        
        Args:
            task: "analysis", "planning", o "vision"
        
        Returns:
            Nombre del modelo
        """
        return self.config.get(task, "mistral")
    
    def set_model(self, task: str, model: str) -> None:
        """
        Configura modelo personalizado para una tarea
        
        Args:
            task: "analysis", "planning", o "vision"
            model: Nombre del modelo
        """
        self.config[task] = model
    
    def get_llm(self, task: str) -> OllamaLLM:
        """
        Obtiene instancia de LLM para una tarea
        
        Args:
            task: "analysis", "planning", o "vision"
        
        Returns:
            OllamaLLM configurado
        """
        model_name = self.select(task)
        
        # Cache para evitar crear múltiples instancias
        if model_name not in self.llms:
            self.llms[model_name] = OllamaLLM(model=model_name)
        
        return self.llms[model_name]
    
    def info(self) -> Dict:
        """Retorna información de configuración actual"""
        return {
            "mode": self.mode,
            "config": self.config,
            "models_info": {
                task: self.MODELS_INFO.get(model, {})
                for task, model in self.config.items()
            }
        }
    
    def print_info(self) -> None:
        """Imprime información formateada"""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        
        table = Table(title=f"Model Configuration - Mode: {self.mode}")
        table.add_column("Tarea", style="cyan")
        table.add_column("Modelo", style="green")
        table.add_column("Tamaño", style="yellow")
        table.add_column("Velocidad", style="blue")
        table.add_column("Calidad", style="magenta")
        
        for task, model in self.config.items():
            info = self.MODELS_INFO.get(model, {})
            table.add_row(
                task,
                model,
                info.get("size", "N/A"),
                info.get("speed", "N/A"),
                info.get("quality", "N/A")
            )
        
        console.print(table)


# Atajos para uso rápido
def get_model_for_task(task: str, mode: str = "balanced") -> str:
    """Función auxiliar rápida"""
    selector = ModelSelector(mode=mode)
    return selector.select(task)


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== NIVEL 1: Selector Básico ===\n")
    
    # Modo balanced (default)
    selector = ModelSelector()
    selector.print_info()
    
    print("\n--- Cambiar a modo speed ---\n")
    selector = ModelSelector(mode="speed")
    selector.print_info()
    
    print("\n--- Cambiar a modo quality ---\n")
    selector = ModelSelector(mode="quality")
    selector.print_info()
    
    print("\n--- Personalizado ---\n")
    selector = ModelSelector()
    selector.set_model("planning", "dolphin-mixtral")
    selector.print_info()
