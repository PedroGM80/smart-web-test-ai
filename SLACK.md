# Slack Integration - Smart Test

Recibe notificaciones de tests en Slack automáticamente.

---

## 🚀 Setup Rápido (5 minutos)

### Paso 1: Crear Slack App

1. Ve a https://api.slack.com/apps
2. Click **Create New App**
3. Selecciona **From scratch**
4. Nombre: "Smart Test"
5. Workspace: Tu workspace
6. Click **Create App**

### Paso 2: Habilitar Webhooks

1. En el menú izquierdo: **Incoming Webhooks**
2. Toggle para activar
3. Click **Add New Webhook to Workspace**
4. Selecciona el canal (ej: #testing)
5. Click **Allow**
6. Copia la URL del webhook (empieza con `https://hooks.slack.com/...`)

### Paso 3: Configurar Smart Test

```bash
# Opción 1: Setup interactivo
python slack_integration.py
# Te pedirá el webhook URL

# Opción 2: Archivo .env
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/..." >> .env

# Opción 3: API
curl -X POST "http://localhost:8000/slack/webhook?webhook_url=https://hooks.slack.com/..."
```

---

## 📨 Usar

### Opción 1: CLI

```bash
python smart_test.py "https://github.com" "Test" --slack
```

### Opción 2: Web UI

En Streamlit, hay checkbox para "Enviar a Slack"

### Opción 3: API

```bash
POST /test/with-slack
{
  "url": "https://github.com",
  "objective": "Test repo",
  "mode": "balanced"
}
```

### Opción 4: Automático (si webhook configurado)

Todos los tests van a Slack automáticamente

---

## 📊 Mensajes

### Test Result
```
URL: https://github.com
Objective: Test repository
Pass Rate: 95.5%
Duration: 42.3s
Status: SUCCESS
Mode: balanced
```

### Daily Summary
```
Total Tests: 42
Avg Pass Rate: 93.5%
Avg Duration: 35.2s
Domains: 8
Best Model: mistral
Time Saved: 315h
```

### Error Notification
```
URL: https://example.com
Error: Timeout exceeded
```

---

## 🎨 Mensajes Coloreados

| Pass Rate | Color | Emoji |
|-----------|-------|-------|
| ≥90% | Verde | ✅ |
| 75-89% | Naranja | ⚠️ |
| <75% | Rojo | ❌ |

---

## 🔧 Personalización

### Cambiar canal de Slack

```python
from slack_integration import SlackNotifier

# Crea nuevo webhook para otro canal
notifier = SlackNotifier("https://hooks.slack.com/...")
notifier.send_test_result(result)
```

### Añadir campos personalizados

```python
message = {
    "attachments": [{
        "fields": [
            {
                "title": "Custom Field",
                "value": "Value",
                "short": True
            }
        ]
    }]
}
```

---

## 📋 Ejemplos

### Enviar desde CLI

```bash
python smart_test.py "https://amazon.com" "Buscar producto"
# Se envía automáticamente a Slack si webhook está configurado
```

### Enviar desde Python

```python
from slack_integration import SlackNotifier

notifier = SlackNotifier()

result = {
    "url": "https://github.com",
    "objective": "Test repo",
    "pass_rate": 95.5,
    "duration": 42.3,
    "status": "success",
    "mode": "balanced"
}

notifier.send_test_result(result)
```

### Enviar resumen diario

```python
from slack_integration import SlackNotifier
from dashboard_analytics import DashboardAnalytics

analytics = DashboardAnalytics()
summary = analytics.get_summary_stats()

notifier = SlackNotifier()
notifier.send_summary(summary)
```

---

## 🔐 Seguridad

### Webhook URL
- Guarda en `.env` (gitignored)
- No commits a Git
- Rotala cada 3 meses

### Permissions
- Solo publica en canal seleccionado
- No puede leer histórico
- No puede acceder a datos personales

---

## 🐛 Troubleshooting

### "Invalid webhook URL"
- Verifica que empiece con `https://hooks.slack.com/`
- Cópiala sin espacios
- Válida en https://api.slack.com/apps

### "Webhook URL not found"
- Check `.env` tiene `SLACK_WEBHOOK_URL=...`
- Reinicia la aplicación
- Usa `python slack_integration.py` para setup

### "Permission denied"
- El app necesita permiso para escribir en el canal
- Vuelve a autorizarlo en Step 2

### No se envía
- Webhook válido: Test en https://api.slack.com/apps
- Red accessible: `curl https://hooks.slack.com/...`
- Requirements: `pip install requests`

---

## 📚 Referencias

- Slack Incoming Webhooks: https://api.slack.com/messaging/webhooks
- Slack Message Format: https://api.slack.com/messaging/composing/layouts
- Slack Colors: https://www.color-hex.com/

---

## 🚀 Próximas Mejoras

- [ ] Slack commands (/smarttest)
- [ ] Message threads
- [ ] Custom emojis
- [ ] Reactions
- [ ] File uploads
- [ ] Interactive buttons
- [ ] Multi-workspace

---

**Slack = Notificaciones en tiempo real donde estás**
