# Email Reports - Smart Test

Envía reportes automáticos bonitos por email cada mañana.

---

## ⚡ Setup Ultra Rápido (3 minutos)

### Para Gmail:

```bash
# 1. Ve aquí:
https://myaccount.google.com/apppasswords

# 2. Selecciona: Mail + Windows
# 3. Copia la contraseña (16 caracteres)

# 4. Ejecuta:
python email_reports.py

# Te pedirá:
# - Tu email
# - App password
```

### Para Outlook/Office 365:

```bash
# Usa: smtp.office365.com:587
# Email + Password normales
```

### Para otros SMTP:

```bash
# Edita .env:
SENDER_EMAIL=tu@email.com
SENDER_PASSWORD=password
SMTP_SERVER=smtp.tuproveedor.com
SMTP_PORT=587
```

---

## 📧 Características

### Daily Report
- ✓ Total de tests
- ✓ Pass rate promedio
- ✓ Duración promedio
- ✓ Dominios analizados
- ✓ Mejor modelo
- ✓ Horas ahorradas
- ✓ HTML bonito
- ✓ Link a dashboard

### Alerts Automáticos
- ✓ High failure rate (< 75%)
- ✓ Timeouts
- ✓ Errores críticos
- ✓ Instantáneos

### Personalización
- ✓ Recipients múltiples
- ✓ Horario customizable
- ✓ Filtros por dominio
- ✓ Templates personalizados

---

## 🚀 Uso

### Opción 1: Enviar manualmente

```python
from email_reports import EmailReporter
from dashboard_analytics import DashboardAnalytics

analytics = DashboardAnalytics()
summary = analytics.get_summary_stats()

reporter = EmailReporter()
reporter.send_daily_report(
    recipients=["boss@company.com", "team@company.com"],
    summary=summary
)
```

### Opción 2: Cron job (automático cada mañana)

```bash
# Edita crontab
crontab -e

# Añade (envía cada día a las 9 AM):
0 9 * * * cd /path/to/smart-test && python -c "from email_reports import EmailReporter; from dashboard_analytics import DashboardAnalytics; EmailReporter().send_daily_report(['boss@company.com'], DashboardAnalytics().get_summary_stats())"
```

### Opción 3: API endpoint

```bash
POST /email/daily-report
{
  "recipients": ["boss@company.com"],
  "schedule": "09:00"  # UTC
}
```

### Opción 4: Alerta en tiempo real

```python
reporter.send_alert(
    recipients=["devops@company.com"],
    alert_type="high_failure_rate",
    details={
        "url": "https://example.com",
        "pass_rate": 45.0,
        "message": "Pass rate dropped below 75%"
    }
)
```

---

## 🎨 Ejemplos de Email

### Daily Report
```
Smart Test Daily Report
Monday, June 07, 2026

Total Tests: 42
Pass Rate: 93.5%
Avg Duration: 35.2s
Domains: 8
Best Model: mistral
Time Saved: 315h
```

### Alert
```
[Alert] Smart Test - High Failure Rate Detected

URL: https://github.com
Timestamp: 2026-06-07 14:32:45
Details: Pass rate dropped to 45%, expected >90%
```

---

## 📋 Configuración

### .env

```bash
# Email sender
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=xyzw1234abcd5678

# SMTP (default: Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Cron schedule (optional)
REPORT_SCHEDULE=0 9 * * *  # 9 AM daily

# Recipients (default: sender)
REPORT_RECIPIENTS=boss@company.com,team@company.com
```

---

## 🔐 Seguridad

### Gmail App Passwords
- ✓ Más seguro que contraseña
- ✓ Se revoca si necesitas
- ✓ No expone contraseña principal
- ✓ Recomendado

### Alertas
- ✓ Solo por email (privado)
- ✓ No se publica en Slack
- ✓ Immediato
- ✓ Configurable

---

## 🐛 Troubleshooting

### "Authentication failed"
- Verifica email/password en .env
- Para Gmail: usa App password, no contraseña
- Test conexión SMTP

### "Connection refused"
- SMTP server/port incorrecto
- Firewall bloqueando puerto 587
- Proveedor requiere SSL (puerto 465)

### "Email not received"
- Check spam folder
- Verifica recipients
- Test enviando a tu propio email

---

## 📊 Impacto

**Adoptación:**
- Managers lo aman (reportes en inbox)
- No necesita dashboard
- Ejecutivos happy
- Word-of-mouth natural

**Diferencial:**
- Stagehand NO TIENE email
- Slack + Email = completo
- Professional = confianza
- Fácil venta

**Automatización:**
- Cron job = sin intervención
- Alertas = awareness
- Dashboard = siempre disponible
- Integración = sin código

---

## 🎯 Pro Tips

### Hack 1: Gmail gratuito
```bash
# Gmail con App password = unlimited emails
# Perfect para MVP/early stage
```

### Hack 2: Alertas selectivas
```python
# Solo alerta si pass_rate < 75%
if summary['avg_pass_rate'] < 75:
    reporter.send_alert(...)
```

### Hack 3: Reportes semanales
```bash
# Cambiar cron a una vez por semana:
0 9 * * 0  # Domingos a las 9 AM
```

### Hack 4: Integrar con Slack
```python
# Primero Slack, si falla entonces email
slack_sent = notifier.send_test_result(result)
if not slack_sent:
    reporter.send_alert(["backup@company.com"], ...)
```

---

## 📈 Roadmap

- [ ] HTML templates personalizados
- [ ] PDF attachments
- [ ] Charts incrustados
- [ ] Multi-language
- [ ] Scheduled reports
- [ ] Digest mode (uno por semana)
- [ ] Integration con Zapier
- [ ] Two-way email (responder)

---

**Email Reports = Reportes profesionales en inbox**
