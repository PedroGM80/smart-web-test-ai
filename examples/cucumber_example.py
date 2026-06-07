#!/usr/bin/env python3
"""
Ejemplo de uso de generación automática de Cucumber features
Demuestra cómo IA genera feature files listos para ejecutar
"""

from agent import SmartTestAgent
from cucumber_generator import CucumberGenerator, StepsGenerator
from rich.console import Console

console = Console()


def example_generate_and_run():
    """Ejemplo: Genera features y muestra cómo ejecutarlas"""
    
    console.print("[bold cyan]Generando Cucumber Features Automáticamente[/bold cyan]\n")
    
    # 1. Ejecuta test con generación de Cucumber
    agent = SmartTestAgent(model="mistral", vision_model="llava")
    
    console.print("[yellow]Paso 1: Analizando página y generando features...[/yellow]")
    
    report = agent.test_web(
        url="https://example.com",
        objectives="Testear página de ejemplo con validaciones completas",
        headless=True,
        generate_cucumber=True  # Genera features automáticamente
    )
    
    # 2. Muestra archivos generados
    console.print("\n[bold cyan]Archivos Generados:[/bold cyan]")
    
    if "cucumber" in report:
        cucumber_info = report["cucumber"]
        console.print(f"Feature: {cucumber_info['feature']}")
        console.print(f"Steps: {cucumber_info['steps']}")
        console.print(f"Dir: {cucumber_info['features_dir']}")
        
        # Lee y muestra el feature generado
        with open(cucumber_info['feature'], 'r') as f:
            feature_content = f.read()
        
        console.print("\n[bold cyan]Feature File Generado:[/bold cyan]")
        console.print("[dim]" + feature_content + "[/dim]")
    
    # 3. Instrucciones para ejecutar
    console.print("\n[bold green]Próximos pasos:[/bold green]")
    console.print("""
[cyan]1. Ejecutar tests con Behave:[/cyan]
   behave features/

[cyan]2. Ejecutar test específico:[/cyan]
   behave features/example_com_testing.feature

[cyan]3. Con reporte HTML:[/cyan]
   behave features/ --format html --outfile report.html

[cyan]4. Ver reporte:[/cyan]
   open report.html
    """)


def example_custom_feature():
    """Ejemplo: Crear feature personalizado manualmente"""
    
    console.print("[bold cyan]Crear Feature Personalizado[/bold cyan]\n")
    
    gen = CucumberGenerator("features")
    
    # Feature personalizado
    custom_feature = """
Feature: Login Functionality
  As a user
  I want to log in
  So that I can access my account

  Background:
    Given the browser is ready

  Scenario: Successful login
    When I navigate to "https://example.com/login"
    Then I should see input fields
    When I fill "username" with "user@example.com"
    And I fill "password" with "password123"
    And I click the login button
    Then I should see "Welcome"

  Scenario: Invalid credentials
    When I navigate to "https://example.com/login"
    And I fill "username" with "user@example.com"
    And I fill "password" with "wrong"
    And I click the login button
    Then I should see an error message
"""
    
    # Guarda feature
    feature_path = gen.save_feature("login_feature", custom_feature)
    console.print(f"[green]Feature guardado:[/green] {feature_path}")
    
    # Genera steps
    steps_gen = StepsGenerator("features")
    steps_path = steps_gen.generate_web_steps()
    console.print(f"[green]Steps generados:[/green] {steps_path}")


def example_run_behave():
    """Ejemplo: Muestra cómo ejecutar Behave"""
    
    console.print("[bold cyan]Ejecutando Tests con Behave[/bold cyan]\n")
    
    console.print("""
[yellow]Comando básico:[/yellow]
  behave features/

[yellow]Con output detallado:[/yellow]
  behave features/ --format plain --no-capture

[yellow]Test específico:[/yellow]
  behave features/example_com_testing.feature

[yellow]Con tags:[/yellow]
  behave features/ -t @smoke

[yellow]Generar reporte HTML:[/yellow]
  behave features/ --format html --outfile report.html

[yellow]Generar JSON para CI/CD:[/yellow]
  behave features/ --format json --outfile results.json

[yellow]Modo parallel (requiere plugin):[/yellow]
  pip install behave-parallel
  behave features/ --parallel
    """)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "generate":
            example_generate_and_run()
        elif example == "custom":
            example_custom_feature()
        elif example == "run":
            example_run_behave()
        else:
            print("Uso: python cucumber_example.py [generate|custom|run]")
    else:
        # Default: muestra info de cómo ejecutar
        example_run_behave()
