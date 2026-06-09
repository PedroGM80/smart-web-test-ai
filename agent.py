"""
Smart Web Test Agent - IA local para testing web automático
Usa Ollama + Playwright para testing inteligente sin código
"""

import os
import base64
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from playwright.sync_api import sync_playwright, Page
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    OllamaLLM = None
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()

console = Console()

class SmartTestAgent:
    """Agente de testing automático con IA local"""
    
    def __init__(self, model: str = None, vision_model: str = None):
        """
        Inicializa el agente
        
        Args:
            model: Modelo para razonamiento (default: mistral)
            vision_model: Modelo con visión (default: llava)
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")
        self.vision_model = vision_model or os.getenv("OLLAMA_VISION_MODEL", "llava")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.llm = OllamaLLM(model=self.model, base_url=self.base_url)
        self.vision_llm = OllamaLLM(model=self.vision_model, base_url=self.base_url)
        
        # Directorios
        self.screenshots_dir = Path(os.getenv("SCREENSHOTS_DIR", "./screenshots"))
        self.reports_dir = Path(os.getenv("REPORTS_DIR", "./reports"))
        
        self.screenshots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        self.test_results = []
    
    def _screenshot_to_base64(self, path: str) -> str:
        """Convierte screenshot a base64"""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    def _log_result(self, status: str, message: str, details: str = ""):
        """Registra resultado de test"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        
        color = "green" if status == "✓" else "red" if status == "✗" else "yellow"
        console.print(f"[{color}]{status}[/{color}] {message}")
    
    def analyze_page(self, page: Page, url: str) -> dict:
        """Analiza página con IA"""
        
        console.print(Panel(f"Analizando: {url}", title="Análisis de Página"))
        
        # Captura HTML
        html = page.content()[:6000]
        
        # IA analiza estructura
        structure_analysis = self.llm.invoke(f"""
Analiza este HTML y proporciona:
1. Elementos principales (botones, inputs, links)
2. Estructura de la página
3. Formularios detectados
4. Potenciales problemas

HTML:
{html}

Sé conciso y directo.
        """)
        
        self._log_result("ℹ", "Estructura analizada")
        
        # Screenshot para visión
        screenshot_path = self.screenshots_dir / f"page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        page.screenshot(path=str(screenshot_path))
        
        # IA analiza visual
        visual_analysis = self.vision_llm.invoke(f"""
Analiza este screenshot y describe:
1. Elementos visuales principales
2. Botones y campos interactuables
3. Errores o problemas visuales
4. Accesibilidad

Sé conciso.
        """)
        
        self._log_result("ℹ", "Análisis visual completado")
        
        return {
            "url": url,
            "html_analysis": structure_analysis,
            "visual_analysis": visual_analysis,
            "screenshot": str(screenshot_path)
        }
    
    def generate_test_plan(self, url: str, objectives: str, page_analysis: dict) -> str:
        """IA genera plan de testing"""
        
        console.print(Panel(f"Objetivo: {objectives}", title="Generando Plan"))
        
        prompt = f"""
Basado en el análisis de página, genera un plan de testing paso a paso.

URL: {url}
Objetivos: {objectives}

Análisis HTML: {page_analysis['html_analysis'][:2000]}
Análisis Visual: {page_analysis['visual_analysis'][:2000]}

Genera pasos específicos y concretos. Incluye:
1. Verificaciones previas
2. Interacciones a realizar
3. Validaciones esperadas
4. Casos de error a probar
        """
        
        plan = self.llm.invoke(prompt)
        self._log_result("ℹ", "Plan generado")
        
        return plan
    
    def generate_actions(self, plan: str, page_analysis: dict) -> list:
        """IA genera acciones Playwright desde el plan"""
        
        console.print(Panel("Generando acciones automáticas", title="Generación"))
        
        prompt = f"""
Basado en este plan de testing y análisis:

Plan: {plan[:2000]}
Análisis: {page_analysis['html_analysis'][:1500]}

Genera una lista de acciones Playwright en este EXACTO formato:
locator|action|value

Acciones posibles:
- fill (rellena input)
- click (hace click)
- check (verifica visible)
- wait (espera elemento)
- screenshot (captura pantalla)
- hover (pasa mouse)
- press (pulsa tecla en el elemento, value=tecla, ej Enter)
- select (elige opción en un dropdown, value=opción)
- goto (navega a URL directa; pon la URL en el campo locator)
- scroll (hace scroll hasta el elemento)

Ejemplos:
input[name="search"]|fill|test query
input[name="search"]|press|Enter
button:has-text("Search")|click|
select#country|select|Spain
.error-message|check|

SOLO ese formato, una acción por línea. Sin explicaciones.
        """
        
        response = self.llm.invoke(prompt)
        
        # Parsea respuesta
        actions = []
        for line in response.split('\n'):
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                actions.append({
                    'locator': parts[0].strip(),
                    'action': parts[1].strip(),
                    'value': parts[2].strip() if len(parts) > 2 else None
                })
        
        self._log_result("ℹ", f"Generadas {len(actions)} acciones")
        return actions
    
    # Action verbs the LLM may use. Kept in one place so the prompt and the
    # executor never drift apart.
    SUPPORTED_ACTIONS = (
        "fill", "click", "check", "wait", "screenshot", "hover",
        "press", "select", "goto", "scroll",
    )

    def execute_actions(self, page: Page, actions: list) -> dict:
        """Ejecuta acciones generadas por IA.

        Returns counts plus `navigated`: True if any action changed the page
        URL, which signals the caller that the DOM analysis is stale and a
        re-observation is needed (multi-step flows).
        """
        
        console.print(Panel(f"Ejecutando {len(actions)} acciones", title="Ejecución"))
        
        results = {
            "total": len(actions),
            "passed": 0,
            "failed": 0,
            "errors": [],
            "navigated": False,
        }
        
        start_url = None
        try:
            start_url = page.url
        except Exception:
            pass
        
        for i, action in enumerate(actions, 1):
            locator = action['locator']
            act = action['action']
            value = action.get('value')
            
            try:
                elem = page.locator(locator)
                
                if act == "fill":
                    elem.fill(value or "")
                    self._log_result("✓", f"[{i}] Fill: {locator}")
                    results["passed"] += 1
                
                elif act == "click":
                    elem.click()
                    self._log_result("✓", f"[{i}] Click: {locator}")
                    results["passed"] += 1
                
                elif act == "check":
                    assert elem.is_visible(), f"No visible"
                    self._log_result("✓", f"[{i}] Check: {locator} visible")
                    results["passed"] += 1
                
                elif act == "wait":
                    page.wait_for_selector(locator, timeout=5000)
                    self._log_result("✓", f"[{i}] Wait: {locator} appeared")
                    results["passed"] += 1
                
                elif act == "screenshot":
                    path = self.screenshots_dir / f"action_{i}_{datetime.now().strftime('%H%M%S')}.png"
                    page.screenshot(path=str(path))
                    self._log_result("✓", f"[{i}] Screenshot saved")
                    results["passed"] += 1
                
                elif act == "hover":
                    elem.hover()
                    self._log_result("✓", f"[{i}] Hover: {locator}")
                    results["passed"] += 1
                
                elif act == "press":
                    # e.g. press Enter on the search box: locator|press|Enter
                    elem.press(value or "Enter")
                    self._log_result("✓", f"[{i}] Press {value or 'Enter'}: {locator}")
                    results["passed"] += 1
                
                elif act == "select":
                    # dropdowns: locator|select|option_value
                    elem.select_option(value or "")
                    self._log_result("✓", f"[{i}] Select '{value}': {locator}")
                    results["passed"] += 1
                
                elif act == "goto":
                    # direct navigation: url|goto|  (locator field carries the URL)
                    page.goto(locator)
                    self._log_result("✓", f"[{i}] Goto: {locator}")
                    results["passed"] += 1
                
                elif act == "scroll":
                    elem.scroll_into_view_if_needed()
                    self._log_result("✓", f"[{i}] Scroll to: {locator}")
                    results["passed"] += 1
                
                else:
                    raise ValueError(f"Unknown action: {act}")
            except Exception as e:
                self._log_result("✗", f"[{i}] {act}: {locator}", str(e))
                results["failed"] += 1
                results["errors"].append({
                    "action": f"{act}:{locator}",
                    "error": str(e)
                })
        
        # Did any action change the page? If so the original analysis is stale.
        try:
            if start_url is not None and page.url != start_url:
                results["navigated"] = True
        except Exception:
            pass
        
        return results
    
    def final_validation(self, page: Page) -> str:
        """IA valida resultado final"""
        
        console.print(Panel("Validación final", title="Análisis"))
        
        page.screenshot(path=str(self.screenshots_dir / "final.png"))
        
        validation = self.vision_llm.invoke(f"""
Analiza el estado final de esta página después de los tests.
¿Hay errores? ¿Funcionó todo? ¿Hay problemas visuales?

Da un veredicto claro: PASÓ o FALLÓ, con razones.
        """)
        
        return validation
    
    def _run_steps(self, page, url: str, objectives: str, max_steps: int = 3) -> dict:
        """Observe -> act -> re-observe loop.

        Each step analyzes the CURRENT page, generates actions for it and
        executes them. If execution navigated to a new page, the next step
        re-analyzes instead of acting on a stale DOM. Stops when there is no
        navigation, no actions are produced, or max_steps is reached.

        Returns aggregated execution results plus the first plan and the
        number of steps taken. Extracted from test_web so it can be unit
        tested with a mocked page/LLM.
        """
        aggregated = {"total": 0, "passed": 0, "failed": 0, "errors": [],
                      "navigated": False}
        first_plan = None
        steps_taken = 0

        for step in range(1, max_steps + 1):
            steps_taken = step
            current_url = url
            try:
                current_url = page.url
            except Exception:
                pass

            # 1. Observe the CURRENT page
            page_analysis = self.analyze_page(page, current_url)

            # 2. Plan (full plan on step 1; later steps continue the objective)
            if step == 1:
                plan = self.generate_test_plan(current_url, objectives, page_analysis)
                first_plan = plan
                console.print(f"\n[cyan]Plan:[/cyan]\n{plan}\n")
            else:
                console.print(f"[cyan]Paso {step}: la página cambió, re-analizando[/cyan]")
                plan = self.generate_test_plan(
                    current_url,
                    f"Continúa con el objetivo: {objectives}. "
                    f"Ya estás en {current_url} tras las acciones anteriores.",
                    page_analysis,
                )

            # 3. Generate actions for the current DOM
            actions = self.generate_actions(plan, page_analysis)
            if not actions:
                break

            # 4. Execute
            step_results = self.execute_actions(page, actions)
            aggregated["total"] += step_results["total"]
            aggregated["passed"] += step_results["passed"]
            aggregated["failed"] += step_results["failed"]
            aggregated["errors"].extend(step_results["errors"])

            # 5. Continue only if we navigated somewhere new
            if not step_results.get("navigated"):
                break
            aggregated["navigated"] = True

        aggregated["steps"] = steps_taken
        return {"execution": aggregated, "plan": first_plan or "",
                "actions_total": aggregated["total"]}

    def test_web(self, url: str, objectives: str, headless: bool = True, 
                 generate_cucumber: bool = False, max_steps: int = 3) -> dict:
        """
        Ejecuta testing automático completo en una URL
        
        Args:
            url: URL a testear
            objectives: Qué testear (descripción)
            headless: Ejecutar sin interfaz gráfica
            generate_cucumber: Generar feature files de Cucumber
        
        Returns:
            Reporte completo del testing
        """
        
        self.test_results = []
        start_time = time.time()
        
        console.print(Panel(
            f"URL: {url}\nObjetivo: {objectives}",
            title="Smart Web Test - Iniciando",
            style="bold blue"
        ))
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                page = browser.new_page()
                page.goto(url)
                
                # Observe -> act -> re-observe loop (multi-step flows)
                run = self._run_steps(page, url, objectives, max_steps=max_steps)
                plan = run["plan"]
                execution_results = run["execution"]
                actions_total = run["actions_total"]
                
                # Validación final
                validation = self.final_validation(page)
                
                # Cucumber needs the last page analysis; reuse a fresh one
                page_analysis = self.analyze_page(page, page.url) if generate_cucumber else None
                
                browser.close()
                
                # Métricas derivadas del resultado de ejecución
                total = execution_results.get("total", 0)
                passed = execution_results.get("passed", 0)
                failed = execution_results.get("failed", 0)
                pass_rate = (passed / total * 100) if total else 0.0
                duration = time.time() - start_time
                
                # Reporte final
                report = {
                    "url": url,
                    "objectives": objectives,
                    "objective": objectives,
                    "plan": plan,
                    "actions_total": actions_total,
                    "steps": execution_results.get("steps", 1),
                    "execution": execution_results,
                    "validation": validation,
                    "results_log": self.test_results,
                    "timestamp": datetime.now().isoformat(),
                    # Contract consumed by the API, CLI and UI
                    "status": "success" if failed == 0 else "failure",
                    "pass_rate": round(pass_rate, 1),
                    "duration": round(duration, 1),
                    "total_actions": total,
                    "passed_actions": passed,
                    "failed_actions": failed,
                }
                
                # Genera Cucumber features si se solicita
                if generate_cucumber:
                    from cucumber_generator import generate_cucumber_files
                    cucumber_files = generate_cucumber_files(
                        url=url,
                        objectives=objectives,
                        page_analysis=page_analysis,
                        plan=plan
                    )
                    report["cucumber"] = cucumber_files
                    self._log_result("ℹ", f"Features Cucumber generados en {cucumber_files['features_dir']}")
                
                self._save_report(report)
                self._print_summary(report)
                
                return report
        
        except Exception as e:
            self._log_result("✗", "ERROR FATAL", str(e))
            console.print(f"[red]Error: {e}[/red]")
            raise
    
    def _save_report(self, report: dict):
        """Guarda reporte en JSON"""
        report_path = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        self._log_result("ℹ", f"Reporte guardado: {report_path}")
    
    def _print_summary(self, report: dict):
        """Imprime resumen visual"""
        
        exec_res = report['execution']
        
        table = Table(title="Resumen de Testing")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("URL", report['url'])
        table.add_row("Acciones", str(exec_res['total']))
        table.add_row("Exitosas", f"[green]{exec_res['passed']}[/green]")
        table.add_row("Fallidas", f"[red]{exec_res['failed']}[/red]")
        table.add_row("Validación", "[green]PASÓ[/green]" if "pasó" in report['validation'].lower() else "[red]FALLÓ[/red]")
        
        console.print("\n")
        console.print(table)
        
        console.print(f"\n[cyan]Validación Final:[/cyan]\n{report['validation']}")


if __name__ == "__main__":
    # Ejemplo de uso
    agent = SmartTestAgent()
    
    report = agent.test_web(
        url="https://github.com/langchain-ai/deepagents",
        objectives="Verificar que la página carga correctamente, analizar estructura, y validar elementos clave"
    )
