#!/bin/bash
# Setup Grafana + InfluxDB

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "================================"
echo "Smart Web Test - Grafana Setup"
echo "================================"
echo ""

# Verifica Docker
echo -e "${YELLOW}Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no encontrado${NC}"
    echo "Instala Docker desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo -e "${GREEN}✓ Docker encontrado${NC}"

# Verifica Docker Compose
echo -e "${YELLOW}Verificando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose no encontrado${NC}"
    echo "Instálalo con: docker install docker-compose-plugin"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose encontrado${NC}"

# Inicia servicios
echo ""
echo -e "${YELLOW}Iniciando servicios...${NC}"
docker-compose up -d

echo -e "${GREEN}✓ Servicios iniciados${NC}"

# Espera a que se inicialice InfluxDB
echo ""
echo -e "${YELLOW}Esperando a que InfluxDB esté listo...${NC}"
sleep 5

# Crea bucket en InfluxDB
echo -e "${YELLOW}Configurando InfluxDB...${NC}"

docker exec smart-test-influxdb influx org create \
    --name smart-test \
    2>/dev/null || echo "Org ya existe"

docker exec smart-test-influxdb influx bucket create \
    --name test_metrics \
    --org smart-test \
    2>/dev/null || echo "Bucket ya existe"

docker exec smart-test-influxdb influx auth create \
    --user admin \
    --org smart-test \
    --token smart-test-token \
    --read-buckets \
    --write-buckets \
    2>/dev/null || echo "Token ya existe"

echo -e "${GREEN}✓ InfluxDB configurado${NC}"

# Espera a Grafana
echo ""
echo -e "${YELLOW}Esperando a que Grafana esté listo...${NC}"
sleep 5

# Verifica Grafana
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Grafana está listo${NC}"
else
    echo -e "${YELLOW}⚠ Grafana aún se está iniciando...${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}Setup completado!${NC}"
echo "================================"
echo ""
echo "Accede a:"
echo -e "  ${GREEN}Grafana:${NC}   http://localhost:3000"
echo -e "  ${GREEN}InfluxDB:${NC}  http://localhost:8086"
echo ""
echo "Credenciales:"
echo "  Usuario: admin"
echo "  Password: admin123"
echo ""
echo "Próximos pasos:"
echo "  1. Ejecuta tests: python smart_test.py \"https://example.com\" \"test\""
echo "  2. Envía métricas: python metrics_collector.py"
echo "  3. Ve el dashboard en Grafana"
echo ""
echo "Para detener:"
echo "  docker-compose down"
echo ""
