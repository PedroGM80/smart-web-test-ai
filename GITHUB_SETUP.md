# Pushear a GitHub

El código está listo para Git. Sigue estos pasos:

## Opción 1: Crear repo desde GitHub UI (más fácil)

1. Ve a https://github.com/new
2. Nombre: `smart-web-test-ai`
3. Descripción: "IA local para testing web automático - Ollama + Playwright"
4. Privado o público (tu elección)
5. **NO** inicialices con README (ya lo tenemos)
6. Click "Create repository"

## Opción 2: Usar GitHub CLI

```bash
gh repo create smart-web-test-ai \
  --source=. \
  --remote=origin \
  --push \
  --public
```

## Push Manual (ambas opciones)

```bash
# Desde dentro de smart-web-test-ai/
cd smart-web-test-ai

# Añade el remote (REEMPLAZA PedroGM80 con tu usuario si es diferente)
git remote add origin https://github.com/PedroGM80/smart-web-test-ai.git

# Cambia a rama main (opcional pero recomendado)
git branch -M main

# Push
git push -u origin main
```

## Si tienes SSH configurado

```bash
git remote add origin git@github.com:PedroGM80/smart-web-test-ai.git
git branch -M main
git push -u origin main
```

## Añade topics/tags (opcional)

En GitHub → Configuración → Topics:
- `ai`
- `testing`
- `ollama`
- `playwright`
- `web-automation`
- `local-llm`

## Listo

Una vez pusheado:
- URL: https://github.com/PedroGM80/smart-web-test-ai
- Otros pueden hacer: `git clone https://github.com/PedroGM80/smart-web-test-ai.git`

---

El commit inicial ya está hecho con:
```
4851cf4 - Initial commit: Smart Web Test AI - IA local para testing web
```
