#!/usr/bin/env python3
"""
Smart Web Test CLI
Uso: python smart_test.py <url> <objective> [--headed]
"""

import sys
import argparse
from rich.console import Console

# The AI agent (Ollama/LangChain) is only needed to actually run a test.
# Import defensively so the module (and persist_report) can be imported and
# tested without that stack installed.
try:
    from agent import SmartTestAgent
except ImportError:
    SmartTestAgent = None

console = Console()


def persist_report(repository, *, url, objective, model, report):
    """Persist a test report through the repository.

    Extracted from main() so it can be tested without the AI agent. Failures
    are swallowed by the caller: persistence must never break a test run.
    """
    return repository.add(
        url=url,
        objective=objective,
        pass_rate=report.get("pass_rate", 0.0),
        duration=report.get("duration", 0.0),
        mode=report.get("mode", "balanced"),
        model=model,
        status=report.get("status", "success"),
    )


def main():
    # Utility subcommands (history/stats/export/compare/config/clear-cache)
    # are dispatched to the CLI module; everything else is "run a test".
    from cli_enhancements import CLI_SUBCOMMANDS, run_cli_command
    if len(sys.argv) > 1 and sys.argv[1] in CLI_SUBCOMMANDS:
        sys.exit(run_cli_command(sys.argv[1:]))
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
    parser.add_argument(
        "--cucumber",
        action="store_true",
        help="Generar feature files de Cucumber/Gherkin"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar el flujo con un agente simulado (sin Ollama ni navegador)"
    )
    
    args = parser.parse_args()
    
    # Validación
    if not args.url.startswith(("http://", "https://")):
        console.print("[red]Error: URL debe empezar con http:// o https://[/red]")
        sys.exit(1)
    
    try:
        if args.dry_run:
            from fake_agent import FakeAgent
            agent = FakeAgent(model=args.model, vision_model=args.vision_model)
            console.print("[bold yellow]Smart Web Test - DRY RUN (agente simulado)[/bold yellow]")
        elif SmartTestAgent is None:
            console.print("[red]Error: el agente no está disponible (falta el stack de IA). Usa --dry-run para probar el flujo.[/red]")
            sys.exit(1)
        else:
            agent = SmartTestAgent(model=args.model, vision_model=args.vision_model)
            console.print("[bold blue]🤖 Smart Web Test - IA Local[/bold blue]")
        console.print(f"URL: {args.url}")
        console.print(f"Objetivo: {args.objective}")
        console.print(f"Modelos: {args.model} + {args.vision_model}\n")
        
        report = agent.test_web(
            url=args.url,
            objectives=args.objective,
            headless=not args.headed,
            generate_cucumber=args.cucumber
        )
        
        # Persist the result so CLI history, the dashboard and the API all
        # see this run. Never let persistence failure break the test run.
        try:
            from database import init_db
            persist_report(
                init_db().tests,
                url=args.url,
                objective=args.objective,
                model=args.model,
                report=report or {},
            )
        except Exception as e:
            console.print(f"[yellow]Aviso: no se pudo guardar el resultado ({e})[/yellow]")
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelado por usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
