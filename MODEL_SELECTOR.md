# Model Selector - De Fácil a Difícil

Sistema inteligente para seleccionar modelos IA locales en Smart Test.

5 niveles de complejidad: **Fácil → Difícil**

---

## NIVEL 1: Básico (10 min)

**Qué es:** Selector simple de modelos por modo

**Archivo:** `model_selector.py`

**Uso:**

```python
from model_selector import ModelSelector

# Modo automático (default)
selector = ModelSelector(mode="balanced")
model = selector.select("planning")  # "mistral"

# Cambiar modo
selector = ModelSelector(mode="speed")
model = selector.select("planning")  # "orca-mini"

# Personalizar
selector = ModelSelector()
selector.set_model("planning", "dolphin-mixtral")
```

**CLI:**

```bash
python smart_test.py --url "..." --optimize balanced
python smart_test.py --url "..." --optimize speed
python smart_test.py --url "..." --optimize quality
```

**Modos disponibles:**

| Modo | Analysis | Planning | Vision |
|------|----------|----------|--------|
| speed | neural-chat | orca-mini | llava-phi |
| balanced | neural-chat | mistral | llava |
| quality | mistral | mistral | llava |

---

## NIVEL 2: Intermedio (15 min)

**Qué es:** Selector interactivo + CLI mejorado

**Archivo:** `smart_test.py` (actualizado)

**Uso:**

```bash
# Ver configuración actual
python smart_test.py --show-models

# Selector interactivo
python smart_test.py --select-models
# Pregunta por cada modelo

# Con benchmark mode
python smart_test.py --url "..." --objective "..." --optimize quality --show-models
```

**Salida:**

```
Modo: balanced

Tarea        Modelo        Tamaño   Velocidad   Calidad
analysis     neural-chat   7B       ⚡⚡        ⭐⭐⭐
planning     mistral       7B       ⚡⚡        ⭐⭐⭐⭐
vision       llava         7B       ⚡⚡        ⭐⭐⭐
```

**Nuevos flags:**

```bash
--optimize {speed,balanced,quality}  Optimización por velocidad/balance/calidad
--select-models                       Selector interactivo
--show-models                         Mostrar configuración actual
```

---

## NIVEL 3: Avanzado (20 min)

**Qué es:** Auto-detección de modelos disponibles

**Archivo:** `model_detector.py`

**Uso:**

```python
from model_detector import ModelDetector

detector = ModelDetector()

# Ver qué modelos tienes
available = detector.get_available_models()
# ["mistral", "neural-chat", "llava"]

# Sugiere configuración óptima
config = detector.suggest_optimal_config()
# {"analysis": "neural-chat", "planning": "mistral", ...}

# Descarga modelos faltantes
detector.download_missing_models(["mistral", "llava"])

# Muestra estado
detector.suggest_setup()
```

**CLI:**

```bash
# Ver estado de modelos
python smart_test.py --detect-models

# Auto-setup (descarga lo necesario)
python smart_test.py --auto-setup
```

**Ventajas:**

✅ Detecta automáticamente qué tienes
✅ Sugiere configuración óptima
✅ Descarga faltantes
✅ No falla por modelos no disponibles

---

## NIVEL 4: Experto (25 min)

**Qué es:** Benchmarking de modelos

**Archivo:** `model_benchmarker.py`

**Uso:**

```python
from model_benchmarker import ModelBenchmarker

benchmarker = ModelBenchmarker()

# Benchmarkea todos los modelos
results = benchmarker.benchmark_models()

# Muestra resultados
benchmarker.show_results()

# Compara lado a lado
benchmarker.compare()

# Recomendaciones
benchmarker.recommend()

# Guarda resultados
benchmarker.save_results("benchmark.json")
```

**CLI:**

```bash
# Benchmarkea todos los modelos
python smart_test.py --benchmark-models

# Benchmarkea específicos
python smart_test.py --benchmark-models mistral neural-chat

# Muestra resultados guardados
python smart_test.py --show-benchmark-results
```

**Salida:**

```
ANÁLISIS
Modelo          Tiempo(s)  Tokens/s
mistral         5.2        42.3
neural-chat     3.1        51.5  ← Más rápido
orca-mini       2.1        38.9

PLANNING
Modelo          Tiempo(s)  Tokens/s
mistral         8.5        45.2  ← Mejor
neural-chat     6.2        39.1
dolphin-mixtral 12.3       61.5

RECOMENDACIONES
Para velocidad: neural-chat
Para calidad: mistral
Para razonamiento: dolphin-mixtral
```

**Métricas:**

- Tiempo de ejecución
- Tokens generados
- Tokens por segundo
- Éxito/fallo

---

## NIVEL 5: Máxima Dificultad (30 min)

**Qué es:** Learning automático - El sistema aprende qué modelo es mejor

**Archivo:** `model_learner.py`

**Uso:**

```python
from model_learner import ModelLearner

learner = ModelLearner()

# Durante los tests, registra resultados
learner.record_result(
    url="https://github.com",
    model="mistral",
    task="analysis",
    duration=5.2,
    success=True,
    tokens=450
)

# Después de varios tests, recomienda
best_model = learner.recommend_model(
    url="https://github.com",
    task="analysis",
    optimize="quality"  # o "speed", "balanced"
)

# Ver estadísticas
learner.print_stats()
```

**Cómo funciona:**

```
Test 1: GitHub + mistral → 5.2s, 450 tokens, éxito
Test 2: GitHub + neural-chat → 3.1s, 380 tokens, éxito
Test 3: GitHub + mistral → 5.0s, 460 tokens, éxito

Learning:
  GitHub + analysis → mistral (mejor histórico)
  GitHub + planning → mistral (mejor histórico)

Próximo test en GitHub:
  Recomendación: mistral (basado en histórico)
```

**Datos guardados:**

```json
{
  "by_domain": {
    "github.com": {
      "mistral": {
        "runs": 10,
        "successes": 9,
        "total_time": 52.5,
        "tasks": {
          "analysis": {"runs": 5, "successes": 5, "avg_time": 5.0},
          "planning": {"runs": 5, "successes": 4, "avg_time": 5.5}
        }
      }
    }
  },
  "total_runs": 10
}
```

**CLI Integration:**

```bash
# Ver estadísticas de learning
python smart_test.py --learning-stats

# Test automático usa learning
python smart_test.py --url "https://github.com" --objective "test" --use-learning

# Resetea learning
python smart_test.py --reset-learning
```

**Ventajas:**

✅ Aprende con el tiempo
✅ Optimiza automáticamente
✅ Por dominio (GitHub vs Amazon vs Custom)
✅ Por tipo de tarea
✅ Historial persistente

---

## FLUJO COMPLETO

```
┌─ NIVEL 1: Seleccionar modo (speed/balanced/quality)
│
├─ NIVEL 2: Ver configuración actual (--show-models)
│
├─ NIVEL 3: Auto-detectar modelos disponibles (--detect-models)
│           └─ Descargar faltantes si es necesario
│
├─ NIVEL 4: Benchmarkear modelos (--benchmark-models)
│           └─ Guardar resultados en benchmark.json
│
└─ NIVEL 5: Learning automático (--use-learning)
            └─ Mejora automáticamente con cada test
```

---

## CÓMO USAR EN AGENT.PY

```python
from model_selector import ModelSelector
from model_learner import ModelLearner

class SmartTestAgent:
    def __init__(self, optimize="balanced", use_learning=False):
        # NIVEL 1: Selector básico
        self.selector = ModelSelector(mode=optimize)
        
        # NIVEL 5: Learning
        self.learner = ModelLearner() if use_learning else None
        
        # Obtén modelos
        analysis_model = self.selector.select("analysis")
        planning_model = self.selector.select("planning")
    
    def test_web(self, url, objectives, ...):
        start = time.time()
        
        # Ejecuta test
        result = self._execute_test(url, objectives)
        
        duration = time.time() - start
        
        # NIVEL 5: Registra resultado
        if self.learner:
            self.learner.record_result(
                url=url,
                model="mistral",
                task="analysis",
                duration=duration,
                success=result.success,
                tokens=result.tokens
            )
        
        return result
```

---

## GUÍA DE SELECCIÓN

**Usa NIVEL 1 (Básico) si:**
- Solo quieres cambiar entre speed/balanced/quality
- No tienes experiencia

**Usa NIVEL 2 (Intermedio) si:**
- Quieres ver qué modelos usarás
- Quieres controlar interactivamente

**Usa NIVEL 3 (Avanzado) si:**
- No sabes qué modelos tienes descargados
- Quieres que auto-detecte y descargue

**Usa NIVEL 4 (Experto) si:**
- Quieres comparar performance real
- Necesitas métricas exactas
- Haces optimización seria

**Usa NIVEL 5 (Máximo) si:**
- Haces muchos tests (50+)
- Quieres optimización automática
- Testeas múltiples dominios

---

## EJEMPLOS PRÁCTICOS

### Ejemplo 1: Usuario Nuevo

```bash
# Nivel 1: Modo simple
python smart_test.py "https://example.com" "test" --optimize balanced
# Listo. Usa defaults inteligentes.
```

### Ejemplo 2: Quiero Control

```bash
# Nivel 2: Selector interactivo
python smart_test.py --select-models
# ¿Modelo para analysis? mistral
# ¿Modelo para planning? dolphin-mixtral
# ¿Modelo para vision? llava
# → Ejecuta test con esa config
```

### Ejemplo 3: Auto-Setup

```bash
# Nivel 3: Auto-detecta
python smart_test.py --detect-models
# ✓ Modelos disponibles: mistral, neural-chat, llava
# ✓ Configuración sugerida: neural-chat + mistral + llava
python smart_test.py ... --auto-setup
```

### Ejemplo 4: Benchmarking

```bash
# Nivel 4: Compara rendimiento
python smart_test.py --benchmark-models
# Resultados:
# - Análisis: neural-chat es 2x más rápido
# - Planning: mistral tiene 15% más tokens
# → Sugiere: neural-chat para analysis, mistral para planning
```

### Ejemplo 5: Production

```bash
# Nivel 5: Learning automático
for url in $(cat urls.txt); do
  python smart_test.py --url "$url" --objective "test" --use-learning
done

# Después de 50 tests:
python smart_test.py --learning-stats
# Muestra qué modelo es mejor para cada dominio
```

---

## Modelo Selector es el Diferencial

Smart Test es mejor que Stagehand porque:

✅ **5 niveles** - Desde simple a ultra-avanzado
✅ **Control total** - Elige qué modelo usar
✅ **Learning automático** - Mejora con la experiencia
✅ **Zero cost** - Todo local
✅ **Flexible** - Adapta a tu caso

Stagehand solo usa Claude (1 modelo, no hay opción).

Smart Test: **Múltiples modelos, optimización infinita.**

---

**Implementado:** 5 módulos + CLI mejorado
**Líneas de código:** ~1,200
**Documentación:** Completa
**Value:** Alto - Diferenciador real
