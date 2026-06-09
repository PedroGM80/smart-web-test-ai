# Smart Web Test - IA Local para Testing Web

[![Tests](https://github.com/PedroGM80/smart-web-test-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/PedroGM80/smart-web-test-ai/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Coverage](https://img.shields.io/badge/coverage-58%25%20measured-yellow.svg)](COVERAGE.md)

Testing web automático usando **IA local** (Ollama) + Playwright. Sin código hardcodeado, sin APIs externas, sin costos.

## Características

- **IA Local**: Usa Ollama (Mistral) para razonamiento
- **Visión**: Llava para análisis de screenshots
- **Automático**: Genera tests sin escribir código
- **Análisis**: Comprende estructura HTML y UI visual
- **CLI**: Interfaz simple por terminal
- **Reportes**: Genera JSON con resultados
- **Cucumber/BDD**: Genera feature files de Gherkin automáticamente
- **Behave**: Tests ejecutables en lenguaje natural
- **Grafana**: Dashboards de métricas en tiempo real
- **InfluxDB**: Base de datos time-series para almacenar métricas
- **RAG**: Aprende automáticamente de tests anteriores (ChromaDB + Embeddings locales)

## Requisitos

- Python 3.9+
- Ollama instalado y ejecutándose
- 2GB RAM mínimo (4GB recomendado)

## Instalación

### Como paquete (recomendado)

```bash
git clone https://github.com/PedroGM80/smart-web-test-ai.git
cd smart-web-test-ai
python3 -m venv .venv && source .venv/bin/activate

pip install -e .              # núcleo: CLI, base de datos, doctor, --dry-run
pip install -e ".[all]"       # todo el stack (Ollama/Playwright/ChromaDB...)
playwright install chromium   # navegadores (solo para ejecución real)

smart-test --help             # comando instalado
smart-test-doctor             # verifica tu entorno
```

Extras disponibles: `[ai]` `[rag]` `[api]` `[ui]` `[metrics]` `[analytics]` `[test]` `[all]`.

### 1. Instala Ollama

```bash
# macOS
brew install ollama

# O desde https://ollama.ai
```

### 2. Descarga modelos

```bash
# Terminal 1: Inicia Ollama
ollama serve

# Terminal 2: Descarga modelos
ollama pull mistral      # Razonamiento
ollama pull llava        # Visión
```

### 3. Instala el proyecto

```bash
unzip smart-web-test-ai.zip
cd smart-web-test-ai

# Entorno virtual
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Instala dependencias
pip install -r requirements.txt

# Instala navegadores
playwright install
```

### 4. Configura variables

```bash
cp .env.example .env
# Edita .env si necesitas cambiar puertos/modelos
```

## Uso

### Probar sin instalar nada (dry-run)

¿No tienes Ollama ni los navegadores de Playwright todavía? Ejecuta el flujo
completo con un agente simulado. Genera un reporte válido y lo persiste, así
puedes ver el ciclo run -> historial -> dashboard funcionando:

```bash
python smart_test.py "https://example.com" "Verificar carga" --dry-run
```

### CLI Simple

```bash
python smart_test.py "https://github.com/langchain-ai/deepagents" "Testear carga y estructura"

python smart_test.py "https://example.com" "Verificar formulario" --headed

python smart_test.py "https://google.com" "Buscar y validar" --model mistral
```

### Opciones

- `--headed`: Muestra navegador (útil para debug)
- `--model`: Modelo Ollama (default: mistral)
- `--vision-model`: Modelo vision (default: llava)
- `--cucumber`: Genera feature files de Cucumber automáticamente

### Cucumber/BDD

Genera feature files ejecutables en Gherkin:

```bash
# Genera features automáticamente
python smart_test.py "https://example.com" "Objetivo" --cucumber

# Ejecuta tests
behave features/

# Reporte HTML
behave features/ --format html --outfile report.html
```

Ver [CUCUMBER.md](CUCUMBER.md) para documentación completa.

### Grafana/InfluxDB

Dashboards con métricas en tiempo real:

```bash
# Inicia Grafana + InfluxDB
docker-compose up -d

# Ejecuta tests
python smart_test.py "https://example.com" "Objetivo"

# Envía métricas a Grafana
python metrics_collector.py

# Accede al dashboard
# http://localhost:3000
```

Ver [GRAFANA.md](GRAFANA.md) para documentación completa.

### RAG - Aprendizaje Automático

Smart Test aprende automáticamente de tests anteriores:

```bash
# Test 1: Guarda patrón en knowledge base
python smart_test.py "https://github.com" "Testear repo"

# Test 2: RAG busca similares y mejora plan automáticamente
python smart_test.py "https://gitlab.com" "Testear repo" --rag
# Result: +7% mejor pass rate sin escribir código nuevo
```

Usa ChromaDB + OllamaEmbeddings (todo local, sin APIs).

Ver [RAG.md](RAG.md) para documentación completa.

### Python Script

```python
from agent import SmartTestAgent

agent = SmartTestAgent()

report = agent.test_web(
    url="https://example.com",
    objectives="Testear login y crear cuenta",
    headless=False  # Ver navegador
)

print(f"Acciones ejecutadas: {report['execution']['passed']}")
print(f"Validación: {report['validation']}")
```

### Tests con Pytest

```bash
pytest test_examples.py -v

# Test específico
pytest test_examples.py::TestSmartAgent::test_github_deepagents -v

# Con output
pytest test_examples.py -v -s
```

## Flujo de Ejecución

1. **Análisis de Página**
   - Lee HTML de la página
   - IA identifica elementos interactuables
   - Captura screenshot

2. **Plan de Testing**
   - IA genera pasos basados en objetivos
   - Analiza estructura y UI visual

3. **Generación de Acciones**
   - IA genera comandos Playwright automáticamente
   - Formato: `locator|action|value`

4. **Ejecución**
   - Ejecuta acciones generadas
   - Registra resultados
   - Captura screenshots

5. **Validación Final**
   - IA valida estado final
   - Genera reporte JSON

## Estructura del Proyecto

```
smart-web-test-ai/
├── agent.py              # Agente principal (SmartTestAgent)
├── smart_test.py         # CLI
├── test_examples.py      # Tests de ejemplo
├── requirements.txt      # Dependencias
├── .env.example          # Variables de entorno
├── README.md             # Este archivo
├── screenshots/          # Capturas durante tests
├── reports/              # Reportes JSON
└── examples/
    └── custom_test.py    # Ejemplo personalizado
```

## Tests

La suite unitaria corre sin Ollama, Playwright ni ChromaDB: los módulos que
dependen de esos servicios usan imports defensivos, y las integraciones
(Slack, email, GitHub, InfluxDB) se prueban con HTTP/SMTP simulados.

```bash
pip install pytest pytest-cov
pytest                              # suite completa
pytest --cov=. --cov-report=term-missing   # con cobertura
```

Cobertura medida actual: **58%** (121 tests). El desglose por módulo y lo que
queda fuera está en [COVERAGE.md](COVERAGE.md). Los scripts de `examples/` y
`test_examples.py` requieren el stack completo y quedan excluidos de la suite
unitaria (ver `pytest.ini`).

## Reportes

Los reportes se guardan en `reports/` como JSON:

```json
{
  "url": "https://github.com/langchain-ai/deepagents",
  "objectives": "Testear carga...",
  "plan": "Plan generado por IA...",
  "actions_total": 12,
  "execution": {
    "total": 12,
    "passed": 10,
    "failed": 2,
    "errors": [...]
  },
  "validation": "Validación final...",
  "timestamp": "2024-01-15T14:32:10.123456"
}
```

## Troubleshooting

### "Connection refused" en Ollama

```bash
# Asegúrate de que Ollama está ejecutándose
ollama serve

# Verifica puerto
curl http://localhost:11434
```

### Modelo no encontrado

```bash
# Lista modelos
ollama list

# Descarga modelo
ollama pull mistral
```

### Timeout en tests

Aumenta timeout en agent.py o reduce tamaño de HTML a analizar:

```python
page.wait_for_selector(locator, timeout=10000)  # 10 segundos
```

### Problemas con Playwright

```bash
# Reinstala navegadores
playwright install --with-deps

# Abre navegador manualmente
python smart_test.py "https://example.com" "test" --headed
```

## Ejemplos Avanzados

### Test con manejo de errores

```python
from agent import SmartTestAgent

agent = SmartTestAgent(model="mistral")

try:
    report = agent.test_web(
        url="https://api.example.com/broken",
        objectives="Verificar manejo de errores"
    )
    
    # Usa resultados
    if report['execution']['failed'] > 0:
        print("Se detectaron errores (esperado)")
    
except Exception as e:
    print(f"Test falló: {e}")
```

### Test múltiples URLs

```python
from agent import SmartTestAgent

agent = SmartTestAgent()

urls = [
    ("https://github.com", "Testear GitHub"),
    ("https://example.com", "Testear ejemplo"),
    ("https://wikipedia.org", "Testear Wiki")
]

for url, obj in urls:
    report = agent.test_web(url, obj)
    print(f"{url}: {report['execution']['passed']} acciones exitosas")
```

## Modelos Recomendados

| Modelo | Uso | Tamaño | RAM | Velocidad |
|--------|-----|--------|-----|-----------|
| mistral | Razonamiento | 7B | 4GB | Rápido |
| neural-chat | Chat/reasoning | 7B | 4GB | Muy rápido |
| orca-mini | Lite | 3B | 2GB | Muy rápido |
| llava | Visión | 7B | 6GB | Normal |
| llava-phi | Visión lite | 3B | 4GB | Rápido |

Para Mac M4 con 8GB RAM: **Mistral + Llava-phi**

## Performance

- **Análisis página**: 3-5s
- **Generación plan**: 5-10s
- **Generación acciones**: 5-10s
- **Ejecución acciones**: 2-30s (depende de interacciones)
- **Validación final**: 3-5s

**Total por test**: 20-60 segundos

## Limitaciones

- Requiere conexión a internet para acceder URLs
- Modelos locales limitan complejidad de razonamiento
- No es sustituto de tests manuales profesionales
- Mejor para smoke tests y validación basic

## Roadmap

- [ ] Soporte para múltiples navegadores
- [ ] Análisis de accesibilidad (WCAG)
- [ ] Performance testing
- [ ] Visual regression testing
- [ ] Integración CI/CD
- [ ] Dashboard web para reportes

## Contribuir

Este es un proyecto abierto. Puedes:
- Reportar bugs
- Sugerir features
- Enviar mejoras

## Licencia

MIT

## Contacto & Support

Para problemas o preguntas:
1. Revisa troubleshooting
2. Verifica logs en `reports/`
3. Ejecuta con `--headed` para debug visual

---

**Happy Testing!** 🤖
