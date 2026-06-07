"""
Cucumber Feature Generator
Convierte análisis de página en feature files de Gherkin
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class CucumberGenerator:
    """Genera feature files de Gherkin desde análisis de IA"""
    
    def __init__(self, features_dir: str = "features"):
        """
        Inicializa generador
        
        Args:
            features_dir: Directorio donde guardar features
        """
        self.features_dir = Path(features_dir)
        self.features_dir.mkdir(exist_ok=True)
        
        # Crear estructura de behave
        self._setup_behave_structure()
    
    def _setup_behave_structure(self):
        """Crea estructura necesaria para behave"""
        
        # Directorio steps
        steps_dir = self.features_dir / "steps"
        steps_dir.mkdir(exist_ok=True)
        
        # environment.py
        env_path = self.features_dir / "environment.py"
        if not env_path.exists():
            env_path.write_text("""
from playwright.sync_api import sync_playwright


def before_all(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)


def before_scenario(context, scenario):
    context.page = context.browser.new_page()


def after_scenario(context, scenario):
    context.page.close()


def after_all(context):
    context.browser.close()
    context.playwright.stop()
""".strip())
    
    def generate_feature(self, 
                        url: str, 
                        objectives: str,
                        page_analysis: Dict,
                        plan: str) -> str:
        """
        Genera feature file desde análisis
        
        Args:
            url: URL testeada
            objectives: Objetivos del testing
            page_analysis: Análisis de página de IA
            plan: Plan generado por IA
        
        Returns:
            Contenido del feature file
        """
        
        # Parsea URL para nombre de feature
        feature_name = self._generate_feature_name(url)
        
        # Genera escenarios
        scenarios = self._generate_scenarios(plan, page_analysis)
        
        # Crea feature file
        feature_content = f"""# Generated feature file
# URL: {url}
# Generated: {datetime.now().isoformat()}

Feature: {feature_name}
  Objective: {objectives}
  
  Background:
    Given the browser is ready
    
{scenarios}
"""
        
        return feature_content.strip()
    
    def _generate_feature_name(self, url: str) -> str:
        """Genera nombre descriptivo de feature desde URL"""
        
        # Extrae dominio
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Limpia
        name = domain.replace("www.", "").replace(".com", "").replace(".org", "")
        
        # Capitaliza
        return f"{name.title()} Testing"
    
    def _generate_scenarios(self, plan: str, analysis: Dict) -> str:
        """Genera escenarios Given/When/Then desde plan"""
        
        scenarios = []
        
        # Extrae elementos del análisis
        html_analysis = analysis.get('html_analysis', '')
        visual_analysis = analysis.get('visual_analysis', '')
        
        # Escenario 1: Carga básica
        scenario1 = """
  Scenario: Page loads successfully
    When I navigate to the page
    Then the page title should not be empty
    And the page should have visible content
"""
        scenarios.append(scenario1)
        
        # Escenario 2: Elementos principales
        if 'botón' in html_analysis.lower() or 'button' in html_analysis.lower():
            scenario2 = """
  Scenario: Main buttons are clickable
    When I navigate to the page
    Then I should see interactive buttons
    And buttons should be clickable
"""
            scenarios.append(scenario2)
        
        # Escenario 3: Formularios
        if 'input' in html_analysis.lower() or 'form' in html_analysis.lower():
            scenario3 = """
  Scenario: Forms are accessible
    When I navigate to the page
    Then I should see input fields
    And input fields should be fillable
"""
            scenarios.append(scenario3)
        
        # Escenario 4: Visual correctness
        scenario4 = """
  Scenario: Visual appearance is correct
    When I navigate to the page
    Then the page should have proper styling
    And text should be readable
    And images should load correctly
"""
        scenarios.append(scenario4)
        
        # Escenario 5: No errors
        scenario5 = """
  Scenario: No JavaScript errors
    When I navigate to the page
    Then the browser console should have no errors
    And the page should be responsive
"""
        scenarios.append(scenario5)
        
        return "\n".join(scenarios)
    
    def save_feature(self, filename: str, content: str) -> Path:
        """
        Guarda feature file
        
        Args:
            filename: Nombre del archivo (sin .feature)
            content: Contenido del feature
        
        Returns:
            Ruta al archivo guardado
        """
        
        # Asegura extensión .feature
        if not filename.endswith(".feature"):
            filename += ".feature"
        
        filepath = self.features_dir / filename
        
        filepath.write_text(content)
        
        return filepath


class StepsGenerator:
    """Genera steps.py con implementaciones automáticas"""
    
    def __init__(self, features_dir: str = "features"):
        self.steps_dir = Path(features_dir) / "steps"
        self.steps_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_web_steps(self) -> Path:
        """Genera web_steps.py con implementaciones"""
        
        content = '''"""
Web testing steps for Behave
Implemented steps for common web testing scenarios
"""

from behave import given, when, then
import time


@given('the browser is ready')
def step_browser_ready(context):
    """Verifica que el navegador está listo"""
    assert context.page is not None
    context.page.set_viewport_size({"width": 1280, "height": 720})


@when('I navigate to the page')
def step_navigate(context):
    """Navega a la URL base"""
    url = context.config.userdata.get('url', 'https://example.com')
    context.page.goto(url)
    context.page.wait_for_load_state('networkidle')


@when('I navigate to "{url}"')
def step_navigate_url(context, url):
    """Navega a una URL específica"""
    context.page.goto(url)
    context.page.wait_for_load_state('networkidle')


@then('the page title should not be empty')
def step_page_title(context):
    """Verifica que hay título"""
    title = context.page.title()
    assert title and len(title) > 0, "Page title is empty"


@then('the page should have visible content')
def step_visible_content(context):
    """Verifica que hay contenido visible"""
    content = context.page.content()
    assert content and len(content) > 100, "Page has no visible content"


@then('I should see interactive buttons')
def step_see_buttons(context):
    """Verifica que hay botones"""
    buttons = context.page.locator('button, [role="button"]')
    count = buttons.count()
    assert count > 0, f"No buttons found"


@then('buttons should be clickable')
def step_buttons_clickable(context):
    """Verifica que botones son clickeables"""
    buttons = context.page.locator('button')
    for i in range(min(3, buttons.count())):  # Prueba primeros 3
        button = buttons.nth(i)
        assert button.is_enabled(), f"Button {i} is not enabled"


@then('I should see input fields')
def step_see_inputs(context):
    """Verifica que hay inputs"""
    inputs = context.page.locator('input, textarea')
    count = inputs.count()
    assert count > 0, "No input fields found"


@then('input fields should be fillable')
def step_inputs_fillable(context):
    """Verifica que inputs son rellenables"""
    inputs = context.page.locator('input[type="text"], textarea')
    for i in range(min(2, inputs.count())):
        input_elem = inputs.nth(i)
        if input_elem.is_visible():
            input_elem.fill("test")
            value = input_elem.input_value()
            assert "test" in value, f"Input {i} is not fillable"


@then('the page should have proper styling')
def step_proper_styling(context):
    """Verifica estilo"""
    # Obtiene elemento body
    body = context.page.locator('body')
    computed_style = body.evaluate('el => window.getComputedStyle(el).backgroundColor')
    assert computed_style, "No styling found"


@then('text should be readable')
def step_text_readable(context):
    """Verifica que texto es legible"""
    text_elements = context.page.locator('p, h1, h2, h3, span')
    count = text_elements.count()
    assert count > 0, "No readable text found"


@then('images should load correctly')
def step_images_load(context):
    """Verifica que imágenes cargan"""
    images = context.page.locator('img')
    
    for i in range(min(5, images.count())):
        img = images.nth(i)
        if img.is_visible():
            # Verifica que tiene src
            src = img.get_attribute('src')
            assert src, f"Image {i} has no src"


@then('the browser console should have no errors')
def step_no_console_errors(context):
    """Verifica que no hay errores en consola"""
    # Almacena errores de consola
    if not hasattr(context, 'console_messages'):
        context.console_messages = []
    
    # Listener de consola
    def on_console_msg(msg):
        if 'error' in msg.type.lower():
            context.console_messages.append(msg.text)
    
    context.page.on('console', on_console_msg)
    
    # Espera un poco
    context.page.wait_for_timeout(1000)
    
    errors = [msg for msg in context.console_messages if 'error' in msg.lower()]
    assert len(errors) == 0, f"Console errors found: {errors}"


@then('the page should be responsive')
def step_responsive(context):
    """Verifica responsividad básica"""
    # Prueba en diferentes tamaños
    sizes = [
        {"width": 1280, "height": 720},  # Desktop
        {"width": 768, "height": 1024},  # Tablet
        {"width": 375, "height": 667},   # Mobile
    ]
    
    original_size = context.page.view_port_size
    
    try:
        for size in sizes:
            context.page.set_viewport_size(size)
            # Verifica que la página es accesible
            body = context.page.locator('body')
            assert body.is_visible(), f"Page not visible at {size}"
    finally:
        # Restaura tamaño original
        if original_size:
            context.page.set_viewport_size(original_size)


@when('I take a screenshot')
def step_take_screenshot(context):
    """Captura screenshot"""
    context.page.screenshot(path="screenshot.png")


@then('the screenshot should be saved')
def step_screenshot_saved(context):
    """Verifica que screenshot se guardó"""
    import os
    assert os.path.exists("screenshot.png")
'''.strip()
        
        filepath = self.steps_dir / "web_steps.py"
        filepath.write_text(content)
        
        return filepath
    
    def generate_init(self):
        """Crea __init__.py en steps"""
        init_file = self.steps_dir / "__init__.py"
        init_file.touch()


def generate_cucumber_files(url: str, 
                           objectives: str,
                           page_analysis: Dict,
                           plan: str,
                           features_dir: str = "features") -> Dict:
    """
    Función principal para generar archivos de Cucumber
    
    Args:
        url: URL testeada
        objectives: Objetivos
        page_analysis: Análisis de página
        plan: Plan de testing
        features_dir: Directorio de features
    
    Returns:
        Dict con rutas de archivos generados
    """
    
    # Genera feature
    feature_gen = CucumberGenerator(features_dir)
    feature_content = feature_gen.generate_feature(
        url, objectives, page_analysis, plan
    )
    
    # Guarda feature
    feature_name = feature_gen._generate_feature_name(url)
    feature_name_slug = feature_name.lower().replace(" ", "_")
    feature_path = feature_gen.save_feature(feature_name_slug, feature_content)
    
    # Genera steps
    steps_gen = StepsGenerator(features_dir)
    steps_path = steps_gen.generate_web_steps()
    steps_gen.generate_init()
    
    return {
        "feature": str(feature_path),
        "steps": str(steps_path),
        "features_dir": str(feature_gen.features_dir)
    }


if __name__ == "__main__":
    # Ejemplo
    analysis = {
        "html_analysis": "Tiene botones y formularios",
        "visual_analysis": "Página bien formateada"
    }
    
    gen = CucumberGenerator()
    feature = gen.generate_feature(
        "https://example.com",
        "Testear ejemplo",
        analysis,
        "Plan de testing"
    )
    
    print(feature)
