# Smart Test API - REST Endpoints

API para ejecutar tests programáticamente.

## Instalación

```bash
pip install fastapi uvicorn
```

## Ejecutar

```bash
uvicorn api:app --reload
```

Abre: `http://localhost:8000/docs` (Swagger UI)

---

## Endpoints

### 1. Health Check

```bash
GET /health
```

Respuesta:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-07T20:00:00"
}
```

### 2. Obtener Modelos Disponibles

```bash
GET /models?mode=balanced
```

Respuesta:
```json
{
  "mode": "balanced",
  "models": {
    "analysis": "neural-chat",
    "planning": "mistral",
    "vision": "llava"
  }
}
```

### 3. Ejecutar Test

```bash
POST /test
```

Request:
```json
{
  "url": "https://github.com",
  "objective": "Testear repositorio",
  "mode": "balanced",
  "generate_cucumber": false,
  "use_rag": true
}
```

Respuesta:
```json
{
  "url": "https://github.com",
  "objective": "Testear repositorio",
  "status": "success",
  "pass_rate": 95.5,
  "total_actions": 15,
  "passed_actions": 15,
  "failed_actions": 0,
  "duration": 42.3,
  "timestamp": "2026-06-07T20:05:00",
  "mode": "balanced"
}
```

### 4. Obtener Resultados

```bash
GET /results?limit=10
```

Respuesta:
```json
{
  "total": 42,
  "limit": 10,
  "results": [...]
}
```

### 5. Obtener Resultado Específico

```bash
GET /results/5
```

### 6. Estadísticas

```bash
GET /stats
```

Respuesta:
```json
{
  "total_tests": 42,
  "avg_pass_rate": 92.5,
  "avg_duration": 35.2,
  "by_mode": {
    "balanced": {"count": 20, "avg_pass_rate": 93.0},
    "speed": {"count": 15, "avg_pass_rate": 88.5},
    "quality": {"count": 7, "avg_pass_rate": 95.0}
  }
}
```

---

## Ejemplos

### cURL

```bash
# Ejecutar test
curl -X POST "http://localhost:8000/test" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com",
    "objective": "Testear repo",
    "mode": "balanced"
  }'

# Ver resultados
curl "http://localhost:8000/results?limit=5"

# Ver estadísticas
curl "http://localhost:8000/stats"
```

### Python

```python
import requests

# Ejecutar test
response = requests.post(
    "http://localhost:8000/test",
    json={
        "url": "https://github.com",
        "objective": "Testear repo",
        "mode": "balanced"
    }
)

result = response.json()
print(f"Pass Rate: {result['pass_rate']}%")
```

### JavaScript/Node.js

```javascript
// Ejecutar test
const response = await fetch('http://localhost:8000/test', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://github.com',
    objective: 'Testear repo',
    mode: 'balanced'
  })
});

const result = await response.json();
console.log(`Pass Rate: ${result.pass_rate}%`);
```

---

## Modos

| Modo | Velocidad | Calidad | Uso |
|------|-----------|---------|-----|
| speed | ⚡⚡⚡ | ⭐⭐ | Tests rápidos |
| balanced | ⚡⚡ | ⭐⭐⭐ | Default |
| quality | ⚡ | ⭐⭐⭐⭐ | Máxima precisión |

---

## Almacenamiento

Resultados guardados en `api_results.json`:

```json
[
  {
    "url": "https://github.com",
    "objective": "Testear repo",
    "status": "success",
    "pass_rate": 95.5,
    ...
  }
]
```

---

## Producción

Para deployment:

```bash
# Gunicorn
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Docker
docker run -p 8000:8000 smart-test-api
```

---

**API REST = Integración fácil con cualquier plataforma**
