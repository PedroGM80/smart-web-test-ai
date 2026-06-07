# Ejemplos de Smart Test

Colección de ejemplos para diferentes features de Smart Test.

## Contenido

### custom_test.py
Ejemplos personalizados y avanzados de testing.

```bash
python examples/custom_test.py github
python examples/custom_test.py multiple
python examples/custom_test.py custom
```

**Ejemplos:**
- `github` - Test avanzado en GitHub Deepagents
- `multiple` - Testing en múltiples sitios
- `custom` - Test con objetivos específicos

### cucumber_example.py
Ejemplos de generación de Cucumber/Gherkin features.

```bash
python examples/cucumber_example.py generate
python examples/cucumber_example.py custom
python examples/cucumber_example.py run
```

**Ejemplos:**
- `generate` - Generar features automáticamente
- `custom` - Crear feature personalizado
- `run` - Ejecutar con Behave

### grafana_example.py
Ejemplos de integración con Grafana + InfluxDB.

```bash
python examples/grafana_example.py workflow
python examples/grafana_example.py batch
python examples/grafana_example.py grafana
```

**Ejemplos:**
- `workflow` - Flujo completo: Test → Grafana
- `batch` - Múltiples tests con métricas
- `grafana` - Cómo acceder al dashboard

### rag_example.py
Ejemplos de RAG - Aprendizaje automático con ChromaDB.

```bash
python examples/rag_example.py basic
python examples/rag_example.py improve
python examples/rag_example.py insights
python examples/rag_example.py workflow
python examples/rag_example.py export
```

**Ejemplos:**
- `basic` - Guardar y buscar tests similares
- `improve` - Mejora automática de planes
- `insights` - Estadísticas y recomendaciones
- `workflow` - Pipeline completo con RAG
- `export` - Exportar knowledge base

## Quick Start

### 1. Ejecuta tu primer test

```bash
python smart_test.py "https://github.com" "Testear repo"
```

### 2. Ve ejemplos

```bash
python examples/custom_test.py github
```

### 3. Explora todas las features

```bash
# Cucumber
python examples/cucumber_example.py generate
behave features/

# Grafana
docker-compose up -d
python examples/grafana_example.py workflow

# RAG
python examples/rag_example.py workflow
```

## Estructura

```
examples/
├── custom_test.py      # Tests personalizados
├── cucumber_example.py # BDD/Gherkin examples
├── grafana_example.py  # Dashboards y métricas
├── rag_example.py      # Aprendizaje automático
└── README.md           # Este archivo
```

## Flujo de Aprendizaje Recomendado

1. **Básico**
   - `python smart_test.py "URL" "Objetivo"`
   - Ver QUICKSTART.md

2. **Intermedio**
   - `python examples/custom_test.py github`
   - `python examples/cucumber_example.py generate`
   - Ver CUCUMBER.md

3. **Avanzado**
   - `docker-compose up -d`
   - `python examples/grafana_example.py workflow`
   - `python examples/rag_example.py workflow`
   - Ver GRAFANA.md y RAG.md

4. **Experto**
   - Customizar en `custom_test.py`
   - Crear dashboards personalizados en Grafana
   - Optimizar RAG para tu caso de uso

## Requisitos

Todos los ejemplos requieren:
- Python 3.9+
- Ollama ejecutándose: `ollama serve`
- Dependencias instaladas: `pip install -r requirements.txt`
- Navegadores de Playwright: `playwright install`

## Troubleshooting

### "ModuleNotFoundError: No module named 'agent'"

Asegúrate de ejecutar desde el directorio raíz:
```bash
cd smart-web-test-ai
python examples/custom_test.py
```

### "Connection refused" - Ollama

```bash
# En otra terminal
ollama serve

# O con Docker
docker run -d -p 11434:11434 ollama/ollama
```

### Docker no funciona

Para Grafana:
```bash
# Instala Docker Desktop: https://www.docker.com/products/docker-desktop
# O Docker en Linux: https://docs.docker.com/engine/install/
```

## Contribuir

Para añadir más ejemplos:

1. Crea nuevo archivo en `examples/`
2. Sigue el patrón de otros archivos
3. Incluye docstrings y comentarios
4. Actualiza este README

## Contacto

Para preguntas sobre ejemplos:
- Lee la documentación principal (README.md)
- Revisa el código del ejemplo
- Busca en GitHub issues
