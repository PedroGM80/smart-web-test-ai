# Analytics Dashboard - Smart Test

Dashboard visual interactivo para analizar rendimiento y ROI de testing automático.

---

## 🚀 Inicio Rápido

### Opción 1: Desde navegador

```bash
# Inicia API
uvicorn api:app --reload

# Abre en navegador
open dashboard.html
# O: http://localhost:8000/dashboard.html
```

### Opción 2: Servidor estático

```bash
# Python
python -m http.server 8000

# Abre
open http://localhost:8000/dashboard.html
```

### Opción 3: Docker

```bash
docker-compose --profile full up -d

# Dashboard disponible en:
# http://localhost:8000/dashboard/data (datos JSON)
```

---

## 📊 Características

### 1. Estadísticas Resumidas
- **Total de Tests**: Cantidad de tests ejecutados
- **Pass Rate Promedio**: Porcentaje de éxito general
- **Duración Promedio**: Tiempo promedio por test
- **Dominios Analizados**: Cantidad de sitios web únicos
- **Mejor Modelo**: IA que mejor rendimiento tiene
- **Tiempo Ahorrado**: Horas ahorradas en testing

### 2. Gráficos

#### Pass Rate Trend (7 días)
```
Muestra: Porcentaje de éxito por día
Tipo: Gráfico de línea
Uso: Ver tendencia de calidad
```

#### Comparativa de Modelos
```
Muestra: Success rate por modelo
Tipo: Gráfico de barras
Uso: Elegir mejor modelo
```

#### Distribución por Dominio
```
Muestra: Tests por sitio web
Tipo: Gráfico de donuts
Uso: Ver dominios más testeados
```

#### Distribución por Modo
```
Muestra: Tests por modo (speed/balanced/quality)
Tipo: Gráfico de pie
Uso: Analizar preferencias
```

### 3. ROI & Ahorros

| Métrica | Descripción |
|---------|------------|
| Horas Ahorradas | Tiempo que ahorraste vs testing manual |
| Dinero Ahorrado | Costo equivalente en salarios |
| ROI | Return on Investment (%) |
| Payback Period | Días para recuperar inversión |

---

## 💡 Cálculos ROI

### Fórmula

```
Horas Ahorradas = (Testing Manual - Testing Automatizado) × Total Tests
Costo Ahorrado = Horas Ahorradas × Tarifa Horaria ($50/hora)
ROI = (Costo Ahorrado - Costo Setup) / Costo Setup × 100
Payback Period = Costo Setup / (Costo Ahorrado / 30 días)
```

### Supuestos

```
Testing Manual: 30 min por test (0.5 horas)
Testing Automatizado: varía según duración real
Tarifa Horaria: $50/hora
Setup Cost: 20 horas × $50 = $1000
```

### Ejemplo

```
Total Tests: 42
Tiempo automatizado: 35.2s promedio = 0.0098 horas/test
Tiempo manual: 0.5 horas/test

Horas ahorradas = (0.5 - 0.0098) × 42 = 20.6 horas
Costo ahorrado = 20.6 × $50 = $1,030
ROI = ($1,030 - $1,000) / $1,000 × 100 = 3%
Payback Period = $1,000 / ($1,030 / 30) = 29.1 días
```

---

## 🔌 Integración con API

### Endpoint

```
GET /dashboard/data
```

### Response

```json
{
  "summary": {
    "total_tests": 42,
    "avg_pass_rate": 93.5,
    "avg_duration": 35.2,
    "total_time_saved": 1260.5,
    "best_model": "mistral",
    "domains": 8
  },
  "pass_rate_trend": {
    "labels": ["Mon", "Tue", ...],
    "data": [92.0, 93.5, ...]
  },
  "model_performance": {
    "labels": ["mistral", ...],
    "success_rate": [95.5, ...],
    "speed": [3.2, ...],
    "runs": [15, ...]
  },
  "domain_distribution": {
    "labels": ["github.com", ...],
    "data": [12, ...]
  },
  "mode_distribution": {
    "labels": ["balanced", ...],
    "data": [20, ...],
    "colors": ["#4ECDC4", ...]
  },
  "roi": {
    "total_tests": 42,
    "hours_saved": 315,
    "cost_saved": "$6300",
    "net_savings": "$5300",
    "roi_percentage": 265,
    "payback_period_days": 14
  }
}
```

---

## 📝 Personalización

### Cambiar Tarifa Horaria

En `dashboard_analytics.py`:

```python
def calculate_roi(self, manual_test_hours: float = 100) -> Dict:
    hourly_rate = 75  # Cambiar de 50 a 75
```

### Cambiar Duración Manual

```python
hours_per_test_manual = 1  # Cambiar de 0.5 a 1
```

### Cambiar Colores

En `dashboard.html`:

```javascript
backgroundColor: [
    '#667eea',  // Cambiar color
    '#764ba2',
    ...
]
```

---

## 🐛 Troubleshooting

### "Cannot fetch /dashboard/data"
- ❌ API no está ejecutándose
- ✅ Ejecuta: `uvicorn api:app --reload`

### Gráficos no aparecen
- ❌ Sin datos en api_results.json
- ✅ Ejecuta algunos tests: `POST /test`

### Datos de ejemplo
El dashboard fallback automáticamente a datos de ejemplo si la API no está disponible.

### Actualizar datos
Los gráficos se cargan al abrir la página. Para actualizar:
1. Ejecuta nuevos tests
2. Recarga dashboard.html (F5)

---

## 📊 Interpretación de Datos

### Pass Rate Trend
```
Verde/Arriba = Mejora en calidad
Rojo/Abajo   = Degradación
```

Acciones:
- Si baja: revisar cambios recientes
- Si sube: mantener configuración

### Comparativa de Modelos
```
Altura = Success rate
```

Acciones:
- Usa modelo con más altura
- Compara con velocidad
- Balance speed/quality

### Distribución por Dominio
```
Tamaño = Cantidad de tests
```

Acciones:
- Enfoca en dominios grandes
- Aprende patrones por dominio
- Usa Transfer Learning

### ROI Positivo
```
Significa: Ya recuperaste inversión
Beneficio: Cada test adicional es ganancia
```

---

## 🔄 Actualización Automática

Para actualizar dashboard en tiempo real:

```html
<!-- Añadir a dashboard.html en init() -->
setInterval(async () => {
    const data = await loadData();
    updateStats(data);
    // Redraw charts
}, 30000); // Cada 30 segundos
```

---

## 📤 Exportar Datos

### Como JSON
```javascript
// En consola del navegador
JSON.stringify(data)
// Copiar y pegar a archivo
```

### Como CSV
```python
import pandas as pd
results = json.loads(Path("api_results.json").read_text())
df = pd.DataFrame(results)
df.to_csv("results.csv", index=False)
```

### Como PDF Report
```bash
# Usar herramienta tipo wkhtmltopdf
wkhtmltopdf dashboard.html dashboard.pdf
```

---

## 🎯 Casos de Uso

### Para Managers
- Ver ROI y justificar inversión
- Monitorear trends de calidad
- Comparar modelos/configuraciones

### Para QA Engineers
- Identificar modelos mejores
- Detectar dominios problemáticos
- Medir mejoras en tiempo

### Para Executives
- Dashboard de ahorros
- Impacto en productividad
- Business metrics

---

## 🚀 Roadmap Dashboard

- [ ] Real-time updates (WebSocket)
- [ ] Custom date ranges
- [ ] Export to PDF
- [ ] Slack/Email notifications
- [ ] Comparison mode (A/B testing)
- [ ] Custom metrics
- [ ] Team dashboard
- [ ] Mobile responsive menus

---

**Analytics Dashboard = Datos visuales para decisiones mejores**
