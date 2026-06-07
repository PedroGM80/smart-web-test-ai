# Postman Collection - Smart Test API

Colección lista para importar en Postman para testing de la API.

---

## 📥 Importar Colección

### Opción 1: Desde archivo

1. Abre Postman
2. Click **File** → **Import**
3. Selecciona `postman_collection.json`
4. Click **Import**

### Opción 2: Link directo

```
https://raw.githubusercontent.com/PedroGM80/smart-web-test-ai/develop/postman_collection.json
```

1. Abre Postman
2. Click **File** → **Import from Link**
3. Pega el URL
4. Click **Import**

---

## ⚙️ Configuración

### 1. Establecer base_url

La colección usa variable `{{base_url}}` que por default es `http://localhost:8000`.

Para cambiar:

1. Click en la pestaña **Variables** (parte inferior izquierda)
2. Busca `base_url`
3. Cambia el valor si lo necesitas

### 2. Iniciar API

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: API
uvicorn api:app --reload
```

Verifica en: `http://localhost:8000/docs`

---

## 🧪 Requests Disponibles

### Health & Status (2)
- ✅ Health Check
- ✅ Root Info

### Models (3)
- ✅ Get Models - Speed
- ✅ Get Models - Balanced
- ✅ Get Models - Quality

### Tests (5)
- ✅ Execute Test - GitHub
- ✅ Execute Test - Speed Mode
- ✅ Execute Test - Quality Mode
- ✅ Execute Test - LinkedIn
- ✅ Execute Test - Amazon

### Results (5)
- ✅ Get All Results
- ✅ Get Results - Limit 5
- ✅ Get Results - All
- ✅ Get Specific Result #0
- ✅ Get Specific Result #1

### Statistics (1)
- ✅ Get Statistics

---

## 🚀 Flujo Recomendado

### 1. Verifica que API está activa
```
GET /health
```
Esperado: `{"status": "healthy"}`

### 2. Consulta modelos disponibles
```
GET /models?mode=balanced
```

### 3. Ejecuta un test (comienza rápido)
```
POST /test (Speed Mode)
```

### 4. Mira resultados
```
GET /results?limit=5
```

### 5. Ve estadísticas
```
GET /stats
```

### 6. Prueba quality mode
```
POST /test (Quality Mode)
```

### 7. Obtén resultado específico
```
GET /results/0
```

---

## 📝 Ejemplos

### Test Simple

**Request:**
```json
POST /test
{
  "url": "https://github.com",
  "objective": "Testear repositorio",
  "mode": "balanced",
  "generate_cucumber": false,
  "use_rag": true
}
```

**Response (exitosa):**
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

### Ver Resultados

**Request:**
```
GET /results?limit=10
```

**Response:**
```json
{
  "total": 5,
  "limit": 10,
  "results": [
    {
      "url": "https://github.com",
      "pass_rate": 95.5,
      "duration": 42.3,
      ...
    }
  ]
}
```

---

## 🔍 Testing Tips

### 1. Ejecuta antes de cambios
```
GET /health
```

### 2. Valida JSON
Postman valida automáticamente en la pestaña **Tests**

### 3. Usa Variables
Para reutilizar valores en múltiples requests

### 4. Pre-request Scripts
Para setup dinámico antes de ejecutar

### 5. Tests Automáticos
```javascript
// Ejemplo: Validar status code
pm.test("Status is 200", function () {
    pm.response.to.have.status(200);
});
```

---

## 📊 Exportar Resultados

### Como JSON
1. Click derecho en request
2. **Export**
3. Guarda como `results.json`

### Como HTML Report
1. Click en **...** (menu)
2. **Export Collection**
3. Selecciona formato

---

## 🐛 Troubleshooting

### "Cannot GET /test"
- ❌ API no está ejecutándose
- ✅ Ejecuta: `uvicorn api:app --reload`

### "Connection refused"
- ❌ API no está en localhost:8000
- ✅ Verifica variable `base_url`

### "Module not found"
- ❌ Requirements no instalados
- ✅ Ejecuta: `pip install -r requirements.txt`

### Ollama no responde
- ❌ Ollama no está ejecutándose
- ✅ Ejecuta: `ollama serve`

---

## 🔄 Ambiente Múltiple

Para testing en diferentes ambientes:

1. Click en **Manage Environments**
2. Crea nuevo:
   - **Local**: `http://localhost:8000`
   - **Staging**: `https://staging.api.com`
   - **Production**: `https://api.com`

3. Selecciona antes de ejecutar tests

---

## 📚 Referencias

- [API Documentation](API.md)
- [REST Endpoints](API.md#endpoints)
- [Postman Docs](https://learning.postman.com/)

---

**Postman Collection = Testing fácil sin código**
