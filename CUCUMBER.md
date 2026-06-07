# Cucumber/Behave Integration

Testing con Cucumber y Behave - Generación automática de features desde IA.

## Qué es Cucumber/Behave

Cucumber es un framework BDD (Behavior Driven Development) que usa lenguaje natural (Gherkin) para escribir tests.

**Ventajas:**
- Legible para no-técnicos
- Documenta el comportamiento esperado
- Tests ejecutables
- Fácil mantenimiento

## Workflow

```
IA analiza página → Genera plan → Crea .feature files → Behave ejecuta
```

## Uso

### Generar features automáticamente

```bash
python smart_test.py "https://github.com" "Testear repo" --cucumber
```

Crea:
- `features/github_testing.feature` (feature file generado)
- `features/steps/web_steps.py` (steps implementados)
- `features/environment.py` (setup de Behave)

### Ejecutar features

```bash
# Ejecutar todos los tests
behave features/

# Ejecutar feature específico
behave features/github_testing.feature

# Con output detallado
behave features/ --format plain --no-capture

# Generar reporte HTML
behave features/ --format html --outfile report.html
```

## Estructura de Feature File

Generado automáticamente con esta estructura:

```gherkin
Feature: GitHub Testing
  Objective: Testear repositorio
  
  Background:
    Given the browser is ready
  
  Scenario: Page loads successfully
    When I navigate to the page
    Then the page title should not be empty
    And the page should have visible content
  
  Scenario: Main buttons are clickable
    When I navigate to the page
    Then I should see interactive buttons
    And buttons should be clickable
```

## Steps Disponibles

Implementados automáticamente en `features/steps/web_steps.py`:

### Navigation
- `When I navigate to the page`
- `When I navigate to "{url}"`

### Verification
- `Then the page title should not be empty`
- `Then the page should have visible content`
- `Then I should see interactive buttons`
- `Then buttons should be clickable`
- `Then I should see input fields`
- `Then input fields should be fillable`
- `Then the page should have proper styling`
- `Then text should be readable`
- `Then images should load correctly`
- `Then the browser console should have no errors`
- `Then the page should be responsive`

### Screenshots
- `When I take a screenshot`
- `Then the screenshot should be saved`

## Ejemplo completo

### 1. Generar features

```bash
python smart_test.py "https://example.com" "Testear formulario" --cucumber
```

Output:
```
ℹ Features Cucumber generados en features/
```

### 2. Ver feature generado

```bash
cat features/example_com_testing.feature
```

```gherkin
Feature: Example Com Testing
  Objective: Testear formulario
  
  Background:
    Given the browser is ready
  
  Scenario: Page loads successfully
    When I navigate to the page
    Then the page title should not be empty
    And the page should have visible content
  
  Scenario: Forms are accessible
    When I navigate to the page
    Then I should see input fields
    And input fields should be fillable
```

### 3. Ejecutar tests

```bash
behave features/example_com_testing.feature
```

Output:
```
Feature: Example Com Testing
  Scenario: Page loads successfully
    When I navigate to the page ... passed in 2.5s
    Then the page title should not be empty ... passed in 0.1s
    And the page should have visible content ... passed in 0.1s
  
  Scenario: Forms are accessible
    When I navigate to the page ... passed in 2.3s
    Then I should see input fields ... passed in 0.2s
    And input fields should be fillable ... passed in 0.3s

2 features passed, 0 failed
```

## Crear custom steps

Edita `features/steps/web_steps.py`:

```python
from behave import when, then

@when('I fill "{field}" with "{value}"')
def step_fill_field(context, field, value):
    context.page.fill(f'input[name="{field}"]', value)

@then('I should see "{text}"')
def step_see_text(context, text):
    context.page.wait_for_selector(f'text={text}')
    assert context.page.locator(f'text={text}').is_visible()
```

Luego usa en features:

```gherkin
Scenario: Fill form
  When I navigate to the page
  And I fill "email" with "test@test.com"
  Then I should see "Welcome"
```

## Integración con CI/CD

### GitHub Actions

```yaml
name: BDD Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: behave features/
```

### GitLab CI

```yaml
test:
  script:
    - pip install -r requirements.txt
    - behave features/
```

## Reports

### HTML Report

```bash
behave features/ --format html --outfile reports/index.html
```

Abre `reports/index.html` en navegador.

### JSON Report (para procesamiento)

```bash
behave features/ --format json --outfile reports/results.json
```

## Troubleshooting

### "No steps were executed"

Verifica que `features/steps/` tiene `__init__.py`:
```bash
touch features/steps/__init__.py
```

### "Undefined steps"

Tus step definitions no match con los steps del feature. Verifica:
1. Nombres exactos
2. Parámetros entre comillas
3. Espacios/capitalización

### "Browser not found"

Asegúrate de instalar navegadores:
```bash
playwright install
```

### Timeout en tests

Aumenta timeout en `features/environment.py` o en steps:
```python
context.page.set_default_timeout(10000)  # 10 segundos
```

## Tips

1. **Mantenga features simples** - 1 comportamiento por scenario
2. **Use Background** - Para setup común
3. **Nombres descriptivos** - Que expliquen qué se prueba
4. **DRY (Don't Repeat Yourself)** - Reutiliza steps
5. **Tags** - Para organizar tests:

```gherkin
@smoke @critical
Scenario: Login
```

Ejecutar solo tagged:
```bash
behave features/ -t @smoke
```

## Recursos

- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)
- [Playwright Python](https://playwright.dev/python/)
- [BDD Best Practices](https://cucumber.io/docs/bdd/)

---

**Happy BDD Testing!** 🚀
