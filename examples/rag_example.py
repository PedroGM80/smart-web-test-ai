#!/usr/bin/env python3
"""
Ejemplos de RAG en Smart Test
Demuestra cómo Smart Test aprende automáticamente de tests anteriores
"""

from pathlib import Path
from knowledge_base import TestKnowledgeBase
from rag_optimizer import RAGOptimizer
from agent import SmartTestAgent
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def example_basic_rag():
    """Ejemplo básico: Guardar test y buscar similares"""
    
    console.print(Panel(
        "Ejemplo 1: RAG Básico",
        title="Smart Test + RAG",
        style="bold cyan"
    ))
    
    # Crea knowledge base
    kb = TestKnowledgeBase()
    
    # Simula test completado
    console.print("\n[cyan]Guardando test completado...[/cyan]")
    
    kb.store_test(
        url="https://github.com/langchain-ai/deepagents",
        objectives="Testear repositorio GitHub",
        plan="""
        1. Cargar página del repositorio
        2. Verificar que el título contiene 'deepagents'
        3. Buscar sección de README
        4. Verificar botones de acción (Watch, Star, Fork)
        5. Validar que los links son accesibles
        6. Capturar estado final
        """,
        results={
            "total_actions": 15,
            "passed_actions": 15,
            "failed_actions": 0,
            "pass_rate": 100.0
        }
    )
    
    # Busca similares
    console.print("\n[cyan]Buscando tests similares para otro repo GitHub...[/cyan]")
    
    similar = kb.find_similar_tests(
        url="https://github.com/facebook/react",
        objectives="Testear repositorio GitHub"
    )
    
    if similar:
        console.print(f"\n[green]✓ Encontrados {len(similar)} tests similares[/green]")
        for i, test in enumerate(similar, 1):
            console.print(f"\n[dim]Test {i}:[/dim]")
            console.print(f"  URL: {test['url']}")
            console.print(f"  Pass Rate: {test['pass_rate']:.1f}%")


def example_plan_improvement():
    """Ejemplo 2: Mejora automática de planes"""
    
    console.print(Panel(
        "Ejemplo 2: Mejora de Planes con RAG",
        title="Smart Test Learning",
        style="bold cyan"
    ))
    
    kb = TestKnowledgeBase()
    optimizer = RAGOptimizer(knowledge_base=kb)
    
    # Plan inicial (generado por IA simple)
    initial_plan = """
    1. Cargar página
    2. Verificar título
    3. Buscar elementos principales
    """
    
    console.print("\n[cyan]Plan inicial (básico):[/cyan]")
    console.print(f"[dim]{initial_plan}[/dim]")
    
    # Mejora con RAG
    console.print("\n[cyan]Mejorando plan con RAG...[/cyan]")
    
    improved_plan = optimizer.improve_plan(
        url="https://example.com",
        initial_plan=initial_plan,
        objectives="Testear página web"
    )
    
    console.print("\n[green]Plan mejorado (con patrones):[/green]")
    console.print(f"[dim]{improved_plan}[/dim]")


def example_insights():
    """Ejemplo 3: Obtener insights sobre historial de testing"""
    
    console.print(Panel(
        "Ejemplo 3: Insights y Estadísticas",
        title="Smart Test Analytics",
        style="bold cyan"
    ))
    
    kb = TestKnowledgeBase()
    optimizer = RAGOptimizer(knowledge_base=kb)
    
    # Obtén insights
    console.print("\n[cyan]Analizando historial de tests en GitHub...[/cyan]")
    
    insights = optimizer.get_insights("https://github.com/some/repo")
    
    # Muestra estadísticas
    if insights["statistics"]:
        stats = insights["statistics"]
        
        table = Table(title="Estadísticas de Testing - GitHub.com")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Dominio", stats.get("domain", "N/A"))
        table.add_row("Total Tests", str(stats.get("total_tests", 0)))
        table.add_row("Tests Exitosos", str(stats.get("successful_tests", 0)))
        table.add_row("Pass Rate Promedio", f"{stats.get('avg_pass_rate', 0):.1f}%")
        table.add_row("Mejor Pass Rate", f"{stats.get('best_pass_rate', 0):.1f}%")
        table.add_row("Peor Pass Rate", f"{stats.get('worst_pass_rate', 0):.1f}%")
        
        console.print(table)
    
    # Sugerencias
    if insights["recommendations"]:
        console.print("\n[cyan]Recomendaciones:[/cyan]")
        for rec in insights["recommendations"]:
            console.print(f"  {rec}")


def example_full_workflow():
    """Ejemplo 4: Workflow completo - Test → Knowledge Base → Mejora"""
    
    console.print(Panel(
        "Ejemplo 4: Workflow Completo",
        title="Smart Test Full Pipeline",
        style="bold cyan"
    ))
    
    console.print("""
[cyan]Flujo:[/cyan]
1. Ejecutar Test 1
2. Guardar en Knowledge Base
3. Ejecutar Test 2 (similar)
4. RAG busca Test 1
5. Mejora automática del plan
6. Mejor resultado

[yellow]Simulación:[/yellow]
    """)
    
    kb = TestKnowledgeBase()
    optimizer = RAGOptimizer(knowledge_base=kb)
    
    # Test 1
    console.print("\n[bold]TEST 1: GitHub Repo[/bold]")
    console.print("[cyan]Ejecutando...[/cyan]")
    
    kb.store_test(
        url="https://github.com/langchain-ai/deepagents",
        objectives="Testear repo",
        plan="1. Cargar\n2. Verificar\n3. Validar",
        results={
            "total_actions": 12,
            "passed_actions": 12,
            "failed_actions": 0,
            "pass_rate": 100.0
        }
    )
    
    console.print("[green]✓ TEST 1 completado: 100% pass rate[/green]")
    console.print("[green]✓ Guardado en Knowledge Base[/green]")
    
    # Test 2 con RAG
    console.print("\n[bold]TEST 2: GitHub Repo Similar[/bold]")
    console.print("[cyan]Buscando tests similares...[/cyan]")
    
    similar = kb.find_similar_tests(
        url="https://github.com/facebook/react",
        objectives="Testear repo",
        k=1
    )
    
    if similar:
        console.print(f"[green]✓ Encontrado test similar: {similar[0]['url']}[/green]")
        console.print(f"  Pass rate histórico: {similar[0]['pass_rate']:.1f}%")
    
    console.print("[cyan]Mejorando plan con RAG...[/cyan]")
    
    initial_plan = "1. Cargar\n2. Verificar"
    improved = optimizer.improve_plan(
        url="https://github.com/facebook/react",
        initial_plan=initial_plan,
        objectives="Testear repo"
    )
    
    console.print("[green]✓ Plan mejorado con patrones de Test 1[/green]")
    console.print("[cyan]Ejecutando TEST 2 con plan mejorado...[/cyan]")
    
    console.print("[green]✓ TEST 2 completado: 98% pass rate (mejora de 13%)[/green]")


def example_export_knowledge():
    """Ejemplo 5: Exportar y respaldar knowledge base"""
    
    console.print(Panel(
        "Ejemplo 5: Exportar Knowledge Base",
        title="Smart Test Backup",
        style="bold cyan"
    ))
    
    kb = TestKnowledgeBase()
    
    console.print("\n[cyan]Exportando knowledge base...[/cyan]")
    
    kb.export_knowledge("knowledge_backup.json")
    
    console.print("[green]✓ Knowledge base exportado[/green]")
    console.print("[dim]Archivo: knowledge_backup.json[/dim]")
    
    # Muestra estadísticas del archivo
    try:
        import json
        with open("knowledge_backup.json") as f:
            data = json.load(f)
        
        console.print(f"\n[cyan]Contenido del backup:[/cyan]")
        console.print(f"  Total tests: {data.get('total_tests', 0)}")
        console.print(f"  Exportado en: {data.get('exported_at', 'N/A')}")
    except:
        pass


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "basic":
            example_basic_rag()
        elif example == "improve":
            example_plan_improvement()
        elif example == "insights":
            example_insights()
        elif example == "workflow":
            example_full_workflow()
        elif example == "export":
            example_export_knowledge()
        else:
            print("Uso: python rag_example.py [basic|improve|insights|workflow|export]")
    else:
        # Ejecuta todos los ejemplos
        example_basic_rag()
        console.print("\n" + "="*60 + "\n")
        example_plan_improvement()
        console.print("\n" + "="*60 + "\n")
        example_insights()
        console.print("\n" + "="*60 + "\n")
        example_full_workflow()
