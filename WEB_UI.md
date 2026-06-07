# Web UI - Smart Test

Interfaz visual para ejecutar tests sin usar CLI.

## Instalación

```bash
pip install streamlit
```

## Usar

```bash
streamlit run smart_test_ui.py
```

Abre tu navegador en: `http://localhost:8501`

---

## Características

### 1. **Ejecutar Tests**
- Input URL + Objetivo
- Selector de modo (speed/balanced/quality)
- Ver modelos seleccionados
- Opciones avanzadas

### 2. **Resultados en Vivo**
- Barra de progreso
- Métricas: pass rate, acciones, duración
- Detalles de análisis
- Errores y warnings

### 3. **Demo**
- Ejecutar demo sin Ollama
- Ver ejemplo de resultado
- Explorar funcionalidades

### 4. **Historial**
- Ver últimos 10 tests
- Estadísticas agregadas
- Filtrar por modo/dominio

### 5. **Configuración**
- Selector de modelos
- Modo de optimización
- Opciones avanzadas (RAG, Cucumber)

---

## Estructura

```
smart_test_ui.py
├── Sidebar
│   ├── Selector de modo (speed/balanced/quality)
│   ├── Modelos seleccionados
│   ├── Opciones avanzadas
│   └── Estadísticas Learning
├── Main
│   ├── URL + Objetivo
│   ├── Botones (Ejecutar, Demo, Historial)
│   ├── Resultado (métricas + detalles)
│   └── Historial (tabla + estadísticas)
└── Footer
```

---

## Flujo de Ejecución

```
1. Usuario ingresa URL + Objetivo
2. Selecciona modo (speed/balanced/quality)
3. Click "Ejecutar"
4. Smart Test:
   a. Analiza página
   b. Genera plan
   c. Ejecuta acciones
   d. Valida resultados
5. Muestra resultados
6. Guarda en historial
```

---

## Demo

```bash
streamlit run smart_test_ui.py
# Click "Demo"
# Ver ejemplo sin ejecutar
```

---

## Historial Persistente

Los tests se guardan en `test_history.json`:

```json
[
  {
    "timestamp": "2026-06-07T19:45:00",
    "url": "https://github.com",
    "objective": "Testear repo",
    "pass_rate": 95.5,
    "duration": 42.3,
    "model_mode": "balanced"
  }
]
```

---

## Próximas Mejoras

- [ ] Compartir resultados (export JSON/PDF)
- [ ] Colaboración en tiempo real (WebSocket)
- [ ] Integración con GitHub/Slack
- [ ] Gráficos de tendencias
- [ ] Alertas automáticas
- [ ] A/B testing de modelos

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'agent'"

Ejecuta desde el directorio raíz:
```bash
cd smart-web-test-ai
streamlit run smart_test_ui.py
```

### "Connection refused" - Ollama

Inicia Ollama en otra terminal:
```bash
ollama serve
```

### Port 8501 ocupado

```bash
streamlit run smart_test_ui.py --server.port 8502
```

---

**Web UI = Máxima usabilidad sin CLI**
