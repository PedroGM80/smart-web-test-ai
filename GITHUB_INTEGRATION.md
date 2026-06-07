# GitHub Integration - Smart Test

Crea issues automáticamente en GitHub cuando los tests fallan.

---

## ⚡ Setup Ultra Rápido (2 minutos)

### Crear Personal Access Token:

```bash
# 1. Ve a:
https://github.com/settings/tokens/new

# 2. Scopes necesarios:
✓ repo (todas las opciones)
✓ read:user

# 3. Genera token

# 4. Copia (no se ve después!)
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 5. Configura:
python github_integration.py

# Te pedirá:
# - Repository (owner/repo)
# - Token
```

---

## 🎯 Features

### Auto Issue Creation
- ✓ Crea issue cuando test falla
- ✓ Pass rate < 75% = issue
- ✓ Incluye error details
- ✓ URL testeada como referencia

### Smart Detection
- ✓ No crea duplicados
- ✓ Busca issues existentes
- ✓ Añade comentarios en updates
- ✓ Auto-labels (bug, critical)

### Issue Management
- ✓ Comentarios automáticos
- ✓ Cierre automático si se arregla
- ✓ Status tracking
- ✓ Histórico completo

### Labels Automáticos
- `smart-test` - Creado por Smart Test
- `automated` - Issue automático
- `critical` - Pass rate < 50%
- `bug` - Pass rate 50-75%

---

## 📋 Flujo

### Failure → Issue

```
Test ejecución
    ↓
Pass rate < 75%
    ↓
GitHubIssueCreator.create_or_update_issue()
    ↓
Busca issue existente
    ↓
Si existe:
    Añade comentario "Still failing"
    ↓
Si no existe:
    Crea nuevo issue
    ↓
GitHub Issues: New issue!
    ↓
Developers ven notificación
```

### Recovery → Close

```
Next test (misma URL)
    ↓
Pass rate >= 75%
    ↓
Auto-close issue
    ↓
Comentario: "Fixed by Smart Test"
    ↓
GitHub: Issue cerrado
```

---

## 🚀 Uso

### Opción 1: Manual

```python
from github_integration import GitHubIssueCreator

creator = GitHubIssueCreator()

result = {
    "url": "https://github.com",
    "objective": "Test repo",
    "pass_rate": 45.0,
    "error": "Timeout exceeded",
    "mode": "balanced",
    "model": "mistral"
}

creator.create_or_update_issue(result)
```

### Opción 2: CLI

```bash
python github_integration.py
```

### Opción 3: Integrado en Smart Test

```python
# En agent.py o api.py:
from github_integration import GitHubIssueCreator

if result['pass_rate'] < 75:
    GitHubIssueCreator().create_or_update_issue(result)
```

### Opción 4: API

```bash
POST /github/create-issue
{
  "url": "https://example.com",
  "objective": "Test something",
  "pass_rate": 45.0,
  "error": "Timeout"
}
```

---

## 📊 Ejemplo de Issue

### Title
```
Test Failure: https://github.com
```

### Body
```
## Test Failure Report

**URL Tested:** https://github.com
**Objective:** Test repository

### Metrics
- Pass Rate: **45.0%**
- Duration: **42.3s**
- Mode: **balanced**
- Model: **mistral**

### Error Details
```
Timeout exceeded after 30 seconds
```

### Timestamp
2026-06-07T18:32:45.123456

---
*Created by Smart Test - AI Testing Platform*
```

### Labels
```
smart-test, automated, critical
```

---

## 🔐 Seguridad

### Token Scope
- ✓ `repo`: Acceso a issues
- ✓ `read:user`: Información básica
- ✗ No necesita `admin` scope
- ✗ No puede: deletear, cambiar settings

### Best Practices
- Token en `.env` (gitignored)
- Regenera cada 3-6 meses
- Un token por aplicación
- Monitorea uso en GitHub

### Revoke Token
```
https://github.com/settings/personal-access-tokens
```

---

## 🔄 DevOps Workflow

### Ejemplo: Auto-remediation

```bash
# 1. Test falla
smart_test.py "https://api.example.com" "Check endpoint"

# 2. Issue creado automáticamente
# GitHub: Issue #123 Created

# 3. Developer ve notificación
# Email: New issue assigned to you

# 4. Developer arregla el problema
# Code commit: Fix API response

# 5. Next test
smart_test.py "https://api.example.com" "Check endpoint"

# 6. Pass rate >= 75%
# Issue #123: Auto-closed
# Comentario: "Fixed by Smart Test"

# 7. Developer: Workflow completo sin intervención
```

---

## 🎯 Casos de Uso

### Caso 1: Monitoreo Contínuo
```
Cron job: Ejecuta tests cada hora
    ↓
Falla → Issue creado
    ↓
Developers alerta (GitHub notifications)
    ↓
Arreglan el problema
    ↓
Next test → Issue auto-cerrado
```

### Caso 2: CI/CD Pipeline
```
GitHub Actions ejecuta tests
    ↓
Si falla → Crear issue
    ↓
Link a PR que causó problema
    ↓
Developers responsables ven issue
    ↓
Arreglan antes de merge
```

### Caso 3: Regresión Detection
```
Baseline test (semanal)
    ↓
Compara vs histórico
    ↓
Regresión detectada → Issue
    ↓
Developers investigtan
    ↓
Cause: Cambio en API
    ↓
Revertir o arreglar
```

---

## 🛠️ Configuración Avanzada

### .env

```bash
# Requerido
GITHUB_REPO=owner/repo
GITHUB_TOKEN=ghp_xxx...

# Opcional
GITHUB_AUTO_CLOSE=true
GITHUB_AUTO_COMMENT=true
GITHUB_MIN_PASS_RATE=75
GITHUB_CRITICAL_THRESHOLD=50
```

### Custom Labels

```python
creator = GitHubIssueCreator()
creator.custom_labels = ["test-failure", "priority:high"]
```

### Multiple Repos

```python
# Crea issues en múltiples repos
repos = ["org/repo1", "org/repo2"]

for repo in repos:
    creator = GitHubIssueCreator(repo=repo)
    creator.create_or_update_issue(result)
```

---

## 📈 Ventajas

### Para Developers
- ✓ Issues directamente en GitHub
- ✓ Parte del workflow normal
- ✓ Notificaciones automáticas
- ✓ Histórico completo

### Para Managers
- ✓ Tracking automático
- ✓ Visibilidad de problemas
- ✓ SLA monitoring
- ✓ Metrics

### Para Equipos
- ✓ Workflow integrado
- ✓ Menos manual work
- ✓ Consistencia
- ✓ Escalable

---

## 🐛 Troubleshooting

### "Token invalid"
- Regenera en: https://github.com/settings/tokens
- Verifica no esté expirado
- Check .env tiene formato correcto

### "Repo not found"
- Verifica owner/repo
- Token tiene acceso al repo
- Repo es público o token tiene acceso

### "Permission denied"
- Token necesita scope `repo`
- Para private repos: token debe ser del dueño
- No puede acceder a issues de otros

### No se crea issue
- Check pass_rate < 75%
- Token válido
- Repo accessible
- Logs en console

---

## 🚀 Próximas Mejoras

- [ ] Close issue cuando test pasa
- [ ] Link a commit
- [ ] Custom templates
- [ ] Jira integration
- [ ] GitLab support
- [ ] Bitbucket support
- [ ] Slack + GitHub sync

---

## 📚 Referencias

- GitHub API: https://docs.github.com/en/rest
- Personal Tokens: https://github.com/settings/tokens
- Issues API: https://docs.github.com/en/rest/issues
- OAuth Scopes: https://docs.github.com/en/developers/apps/scopes

---

**GitHub Integration = Issues automáticas en tu workflow normal**
