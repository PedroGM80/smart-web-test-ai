# Quick Start - 5 minutos

## 1. Setup (2 min)

```bash
# Asegúrate de que Ollama está ejecutándose
ollama serve  # En otra terminal

# En tu terminal principal
unzip smart-web-test-ai.zip
cd smart-web-test-ai

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install
```

## 2. Primer test (1 min)

```bash
python smart_test.py "https://github.com" "Testear carga de página"
```

Eso es todo. La IA:
1. Analiza la página
2. Genera un plan
3. Crea acciones automáticamente
4. Las ejecuta
5. Genera un reporte

## 3. Ver resultados

```bash
# Reportes en JSON
ls -la reports/

# Screenshots
ls -la screenshots/
```

## 4. Ejemplos incluidos

```bash
# Test avanzado
python examples/custom_test.py github

# Múltiples sitios
python examples/custom_test.py multiple

# Tests unitarios
pytest test_examples.py -v
```

## 5. Próximos pasos

1. Edita `.env` si cambias puerto de Ollama
2. Crea tus propios tests en `examples/`
3. Personaliza objetivos según tus necesidades
4. Integra en CI/CD si lo necesitas

## Ayuda

```bash
# Ver opciones CLI
python smart_test.py --help

# Test con navegador visible (debug)
python smart_test.py "https://example.com" "objetivo" --headed

# Cambiar modelo
python smart_test.py "https://example.com" "objetivo" --model neural-chat
```

## Verificar setup

```bash
# ¿Ollama ejecutándose?
curl http://localhost:11434

# ¿Modelos instalados?
ollama list

# ¿Proyecto correctamente?
python -c "from agent import SmartTestAgent; print('✓ OK')"
```

---

¡Listo para testear! 🚀
