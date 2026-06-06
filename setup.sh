#!/bin/bash
# Setup automático para Smart Web Test AI

set -e  # Exit on error

echo "================================"
echo "Smart Web Test AI - Setup"
echo "================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 no encontrado${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Crear venv
echo ""
echo -e "${YELLOW}Creando entorno virtual...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
fi

# Activar venv
source venv/bin/activate

# Instalar dependencias
echo ""
echo -e "${YELLOW}Instalando dependencias...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# Instalar Playwright
echo ""
echo -e "${YELLOW}Instalando navegadores Playwright...${NC}"
playwright install
echo -e "${GREEN}✓ Navegadores instalados${NC}"

# Verificar Ollama
echo ""
echo -e "${YELLOW}Verificando Ollama...${NC}"
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama está ejecutándose${NC}"
else
    echo -e "${YELLOW}⚠ Ollama no está ejecutándose${NC}"
    echo -e "${YELLOW}  Ejecuta en otra terminal: ollama serve${NC}"
fi

# Crear .env
echo ""
echo -e "${YELLOW}Configurando variables de entorno...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env creado${NC}"
else
    echo -e "${GREEN}✓ .env ya existe${NC}"
fi

# Crear directorios
mkdir -p screenshots reports

# Verificar setup
echo ""
echo -e "${YELLOW}Verificando setup...${NC}"
python3 -c "from agent import SmartTestAgent; print('✓ Smart Test Agent importado correctamente')" && \
echo -e "${GREEN}✓ Todo listo${NC}" || \
echo -e "${RED}✗ Error en setup${NC}"

echo ""
echo "================================"
echo -e "${GREEN}Setup completado!${NC}"
echo "================================"
echo ""
echo "Próximos pasos:"
echo "1. Asegúrate de que Ollama está ejecutándose:"
echo "   ollama serve"
echo ""
echo "2. Ejecuta tu primer test:"
echo "   python smart_test.py 'https://example.com' 'Testear carga'"
echo ""
echo "3. Lee QUICKSTART.md para más información"
echo ""
