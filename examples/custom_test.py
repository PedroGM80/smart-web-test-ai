#!/usr/bin/env python3
"""
Ejemplo personalizado - Custom Test
Demuestra cómo usar SmartTestAgent con opciones avanzadas
"""

from agent import SmartTestAgent
from rich.console import Console

console = Console()


def test_github_advanced():
    """Test avanzado: GitHub con múltiples validaciones"""
    
    console.print("[bold cyan]Test Avanzado: GitHub Deepagents[/bold cyan]")
    
    agent = SmartTestAgent(model="mistral", vision_model="llava")
    
    report = agent.test_web(
        url="https://github.com/langchain-ai/deepagents",
        objectives="""
        1. Verificar que la página principal del repo carga
        2. Analizar los elementos principales (código, issues, PRs)
        3. Validar que los botones principales son clickeables
        4. Capturar estado final del repositorio
        """,
        headless=False  # Ver el navegador
    )
    
    # Procesa resultados
    console.print("\n[bold green]Resultados:[/bold green]")
    console.print(f"Total acciones: {report['execution']['total']}")
    console.print(f"Exitosas: {report['execution']['passed']}")
    console.print(f"Fallidas: {report['execution']['failed']}")
    
    if report['execution']['failed'] == 0:
        console.print("[green]✓ Test PASÓ[/green]")
    else:
        console.print("[red]✗ Test FALLÓ[/red]")
        for error in report['execution']['errors']:
            console.print(f"  - {error['action']}: {error['error']}")


def test_multiple_sites():
    """Test múltiples sitios"""
    
    console.print("[bold cyan]Test Múltiples Sitios[/bold cyan]\n")
    
    sites = [
        {
            "url": "https://example.com",
            "objective": "Testear página simple"
        },
        {
            "url": "https://www.python.org",
            "objective": "Analizar sitio Python oficial"
        }
    ]
    
    agent = SmartTestAgent()
    
    results = []
    for site in sites:
        console.print(f"\nTesteando: {site['url']}")
        
        try:
            report = agent.test_web(
                url=site['url'],
                objectives=site['objective']
            )
            
            results.append({
                "url": site['url'],
                "passed": report['execution']['passed'],
                "failed": report['execution']['failed'],
                "status": "✓" if report['execution']['failed'] == 0 else "✗"
            })
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            results.append({
                "url": site['url'],
                "status": "✗",
                "error": str(e)
            })
    
    # Resumen
    console.print("\n[bold cyan]Resumen:[/bold cyan]")
    for result in results:
        status_color = "green" if result['status'] == "✓" else "red"
        console.print(f"[{status_color}]{result['status']}[/{status_color}] {result['url']}")
        if 'passed' in result:
            console.print(f"  Acciones: {result['passed']}/{result['passed'] + result['failed']}")


def test_with_custom_objectives():
    """Test con objetivos muy específicos"""
    
    console.print("[bold cyan]Test con Objetivos Específicos[/bold cyan]")
    
    agent = SmartTestAgent()
    
    # Test enfocado en búsqueda
    report = agent.test_web(
        url="https://www.google.com",
        objectives="""
        Objetivo: Testear funcionalidad de búsqueda
        
        Pasos esperados:
        1. Cargar página de Google
        2. Rellenar campo de búsqueda con 'Ollama'
        3. Hacer click en buscar
        4. Validar que aparecen resultados
        5. Capturar pantalla de resultados
        """,
        headless=False
    )
    
    console.print(f"\n[cyan]Validación Final:[/cyan]\n{report['validation']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        if test_name == "github":
            test_github_advanced()
        elif test_name == "multiple":
            test_multiple_sites()
        elif test_name == "custom":
            test_with_custom_objectives()
        else:
            print("Uso: python custom_test.py [github|multiple|custom]")
    else:
        # Ejecuta el primero por defecto
        test_github_advanced()
