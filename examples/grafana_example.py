#!/usr/bin/env python3
"""
Ejemplo de uso completo: Smart Test + Grafana
Demuestra el flujo: Test → Report → Metrics → Grafana
"""

import subprocess
import time
from pathlib import Path
from agent import SmartTestAgent
from metrics_collector import MetricsCollector
from rich.console import Console
from rich.panel import Panel

console = Console()


def run_complete_workflow():
    """Flujo completo: Testing + Grafana"""
    
    console.print(Panel(
        "Smart Web Test + Grafana - Flujo Completo",
        title="Testing Workflow",
        style="bold blue"
    ))
    
    # 1. Ejecuta tests
    console.print("\n[cyan]Paso 1: Ejecutando tests...[/cyan]")
    
    agent = SmartTestAgent(model="mistral", vision_model="llava")
    
    report = agent.test_web(
        url="https://example.com",
        objectives="Testear página de ejemplo",
        headless=True,
        generate_cucumber=True
    )
    
    # 2. Recolecta métricas
    console.print("\n[cyan]Paso 2: Recolectando métricas...[/cyan]")
    
    collector = MetricsCollector()
    
    # Obtiene último report generado
    reports_dir = Path("reports")
    latest_report = max(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    
    console.print(f"[yellow]Report encontrado: {latest_report.name}[/yellow]")
    
    metrics = collector.collect_from_report(str(latest_report))
    
    console.print("\n[cyan]Métricas recolectadas:[/cyan]")
    for key, value in metrics.items():
        console.print(f"  {key}: {value}")
    
    # 3. Envía a Grafana
    console.print("\n[cyan]Paso 3: Enviando a Grafana...[/cyan]")
    
    if collector.send_metrics(metrics):
        console.print("[green]✓ Métricas enviadas[/green]")
    else:
        console.print("[yellow]⚠ No se pudieron enviar métricas[/yellow]")
        console.print("[yellow]  ¿Grafana está corriendo? docker-compose up -d[/yellow]")
    
    collector.close()
    
    # 4. Instrucciones
    console.print("\n[bold cyan]Próximos pasos:[/bold cyan]")
    console.print("""
1. Ver dashboard en Grafana:
   http://localhost:3000
   
2. Login:
   Usuario: admin
   Password: admin123
   
3. Abre dashboard:
   "Smart Web Test - Testing Metrics"
   
4. Ejecuta más tests para ver tendencias:
   python smart_test.py "https://github.com" "Testear GitHub" 
   python metrics_collector.py
    """)


def run_multiple_tests():
    """Ejecuta múltiples tests y envía métricas a Grafana"""
    
    console.print(Panel(
        "Ejecutando Múltiples Tests",
        title="Batch Testing",
        style="bold cyan"
    ))
    
    sites = [
        ("https://example.com", "Testear ejemplo"),
        ("https://github.com", "Testear GitHub"),
        ("https://python.org", "Testear Python.org"),
    ]
    
    agent = SmartTestAgent()
    collector = MetricsCollector()
    
    results = []
    
    for url, objective in sites:
        console.print(f"\n[cyan]Testing: {url}[/cyan]")
        
        try:
            report = agent.test_web(
                url=url,
                objectives=objective,
                headless=True
            )
            
            # Recolecta y envía métricas
            reports_dir = Path("reports")
            latest_report = max(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
            
            metrics = collector.collect_from_report(str(latest_report))
            collector.send_metrics(metrics)
            
            results.append({
                "url": url,
                "status": "✓",
                "pass_rate": metrics.get("pass_rate", 0)
            })
            
            console.print(f"[green]✓ {url} (Pass Rate: {metrics.get('pass_rate', 0):.1f}%)[/green]")
        
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            results.append({
                "url": url,
                "status": "✗",
                "error": str(e)
            })
        
        time.sleep(2)  # Pausa entre tests
    
    collector.close()
    
    # Resumen
    console.print("\n[bold cyan]Resumen:[/bold cyan]")
    for result in results:
        status_color = "green" if result["status"] == "✓" else "red"
        console.print(f"[{status_color}]{result['status']}[/{status_color}] {result['url']}")
        if "pass_rate" in result:
            console.print(f"    Pass Rate: {result['pass_rate']:.1f}%")


def show_grafana_access():
    """Muestra cómo acceder a Grafana"""
    
    console.print(Panel(
        """
[bold cyan]Grafana Dashboard[/bold cyan]

URL: [bold]http://localhost:3000[/bold]

[cyan]Credenciales:[/cyan]
  Usuario: admin
  Password: admin123

[cyan]Dashboard:[/cyan]
  Smart Web Test - Testing Metrics

[cyan]Componentes:[/cyan]
  • InfluxDB (base de datos): localhost:8086
  • Grafana (visualización): localhost:3000

[cyan]Métricas disponibles:[/cyan]
  • Pass Rate (%)
  • Total Actions
  • Failed Actions  
  • Validation Status
  • Error Count
  • Timeline (últimas 24h)
        """,
        title="Acceso a Grafana",
        style="green"
    ))


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "workflow":
            run_complete_workflow()
        elif example == "batch":
            run_multiple_tests()
        elif example == "grafana":
            show_grafana_access()
        else:
            print("Uso: python grafana_example.py [workflow|batch|grafana]")
    else:
        # Default: muestra acceso
        show_grafana_access()
