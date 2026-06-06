#!/usr/bin/env python3
"""
Smart Web Test CLI
Uso: python smart_test.py <url> <objective> [--headed]
"""

import sys
import argparse
from agent import SmartTestAgent
from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="IA Testing Web - Testing automático con IA local",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python smart_test.py "https://github.com" "Testear carga de página"
  python smart_test.py "https://example.com" "Verificar formulario" --headed
  python smart_test.py "https://google.com" "Buscar y validar resultados" --model mistral
        """
    )
    
    parser.add_argument("url", help="URL a testear")
    parser.add_argument("objective", help="Objetivo del testing (qué testear)")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Ejecutar con navegador visible"
    )
    parser.add_argument(
        "--model",
        default="mistral",
        help="Modelo Ollama a usar (default: mistral)"
    )
    parser.add_argument(
        "--vision-model",
        default="llava",
        help="Modelo vision Ollama (default: llava)"
    )
    
    args = parser.parse_args()
    
    # Validación
    if not args.url.startswith(("http://", "https://")):
        console.print("[red]Error: URL debe empezar con http:// o https://[/red]")
        sys.exit(1)
    
    try:
        agent = SmartTestAgent(model=args.model, vision_model=args.vision_model)
        
        console.print("[bold blue]🤖 Smart Web Test - IA Local[/bold blue]")
        console.print(f"URL: {args.url}")
        console.print(f"Objetivo: {args.objective}")
        console.print(f"Modelos: {args.model} + {args.vision_model}\n")
        
        report = agent.test_web(
            url=args.url,
            objectives=args.objective,
            headless=not args.headed
        )
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelado por usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
