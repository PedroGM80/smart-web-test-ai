# Grafana Integration

Dashboards de testing con Grafana + InfluxDB. Visualización en tiempo real de métricas.

## Setup Rápido

### 1. Instala Docker

- [macOS](https://docs.docker.com/desktop/install/mac-install/)
- [Linux](https://docs.docker.com/engine/install/)
- [Windows](https://docs.docker.com/desktop/install/windows-install/)

### 2. Inicia servicios

```bash
docker-compose up -d
```

Espera 10-15 segundos a que se inicialicen.

### 3. Accede a Grafana

```
http://localhost:3000
```

**Login:**
- Usuario: `admin`
- Password: `admin123`

### 4. Ejecuta tests

```bash
python smart_test.py "https://github.com" "Testear" --cucumber
```

### 5. Envía métricas a Grafana

```bash
python metrics_collector.py
```

O automáticamente después de cada test:
```bash
python smart_test.py "https://example.com" "test" && python metrics_collector.py
```

## Arquitectura

```
SmartTestAgent
    ↓ (genera report JSON)
reports/report_*.json
    ↓
metrics_collector.py
    ↓ (envía métricas)
InfluxDB (almacena)
    ↓
Grafana (visualiza)
    ↓
Dashboard (http://localhost:3000)
```

## Componentes

### InfluxDB
- **Puerto:** 8086
- **Bucket:** test_metrics
- **Organización:** smart-test
- **Token:** smart-test-token
- **Usuario:** admin / admin123

### Grafana
- **Puerto:** 3000
- **Usuario:** admin / admin123
- **Dashboard:** Smart Web Test - Testing Metrics

## Métricas Recolectadas

Cada test reporta:

| Métrica | Descripción | Unidad |
|---------|-------------|--------|
| `total_actions` | Total de acciones ejecutadas | Número |
| `passed_actions` | Acciones exitosas | Número |
| `failed_actions` | Acciones fallidas | Número |
| `pass_rate` | Porcentaje de éxito | % |
| `validation_passed` | Validación final pasó | Bool |
| `errors_count` | Errores encontrados | Número |

## Dashboard Incluido

**Smart Web Test - Testing Metrics**

Paneles:
1. **Pass Rate** - Porcentaje actual de éxito
2. **Total Tests** - Cantidad de tests ejecutados
3. **Failed Actions** - Acciones que fallaron
4. **Pass Rate Over Time** - Gráfica de tendencia (24h)
5. **Actions Status** - Status de acciones en tiempo
6. **URLs Testeadas** - Tabla de URLs testadas

## Usar Métricas

### Recolectar un report específico

```bash
python metrics_collector.py reports/report_20240115_143210.json
```

### Procesar todos los reports

```bash
python metrics_collector.py
```

Procesa automáticamente todos los `.json` en `reports/`

### Desde Python

```python
from metrics_collector import MetricsCollector

collector = MetricsCollector()

# Un report
metrics = collector.collect_from_report("reports/report.json")
collector.send_metrics(metrics)

# Directorio completo
processed = collector.process_reports_dir("reports")

collector.close()
```

## Crear Dashboard Personalizado

### En Grafana UI

1. Click "+" → "Dashboard"
2. "Add a new panel"
3. Selecciona InfluxDB datasource
4. Escribe query en Flux:

```flux
from(bucket: "test_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "test_execution")
  |> filter(fn: (r) => r._field == "pass_rate")
```

5. Customiza visualización
6. Save

### Queries útiles

**Pass rate promedio últimas 24h:**
```flux
from(bucket: "test_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "test_execution")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> mean()
```

**Errores por URL:**
```flux
from(bucket: "test_metrics")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "test_execution")
  |> filter(fn: (r) => r._field == "errors_count")
  |> group(columns: ["url"])
  |> sum()
```

**Tests fallidos hoy:**
```flux
from(bucket: "test_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "test_execution")
  |> filter(fn: (r) => r.validation_passed == 0)
```

## Troubleshooting

### "Connection refused" InfluxDB

```bash
# Verifica que está corriendo
docker ps | grep influxdb

# Reinicia
docker-compose restart influxdb
```

### Grafana no carga dashboard

```bash
# Verifica logs
docker logs smart-test-grafana

# Reinicia
docker-compose restart grafana
```

### Métricas no aparecen

1. Verifica que test se ejecutó: `ls reports/`
2. Ejecuta collector: `python metrics_collector.py`
3. Verifica datos en InfluxDB:

```bash
docker exec -it smart-test-influxdb influx bucket list --org smart-test
```

### Cambiar credenciales

Edita `docker-compose.yml`:

```yaml
environment:
  INFLUXDB_ADMIN_PASSWORD: tuapassword
  GF_SECURITY_ADMIN_PASSWORD: tuapassword
```

Luego: `docker-compose up -d --force-recreate`

## Integración CI/CD

### GitHub Actions

```yaml
name: Tests with Metrics

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      
      - run: pip install -r requirements.txt
      
      - run: python smart_test.py "https://example.com" "test" --cucumber
      
      - name: Send metrics to Grafana
        run: python metrics_collector.py
        if: always()
```

### GitLab CI

```yaml
test:
  script:
    - pip install -r requirements.txt
    - python smart_test.py "https://example.com" "test"
    - python metrics_collector.py
```

## Ports Ocupados

Si los puertos están ocupados, edita `docker-compose.yml`:

```yaml
ports:
  - "8086:8086"  # InfluxDB - cambiar a "8087:8086" si 8086 usado
  - "3000:3000"  # Grafana - cambiar a "3001:3000" si 3000 usado
```

Accede a Grafana en: `http://localhost:3001`

## Detener Servicios

```bash
# Detener
docker-compose down

# Detener y borrar datos
docker-compose down -v
```

## Backup de Datos

```bash
# Backup de InfluxDB
docker exec smart-test-influxdb influx backup /tmp/backup

# Backup de Grafana
docker cp smart-test-grafana:/var/lib/grafana ./grafana-backup
```

## Performance

Con docker-compose en local:
- **Ingesta:** ~100 métricas/segundo
- **Query time:** <1segundo
- **Almacenamiento:** ~1KB por métrica

Para producción, considera:
- Instancia InfluxDB Cloud
- Instancia Grafana Cloud
- Auto-scaling con Kubernetes

## Recursos

- [Grafana Documentation](https://grafana.com/docs/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Flux Language](https://docs.influxdata.com/flux/)
- [Docker Compose](https://docs.docker.com/compose/)

---

**Happy Monitoring!** 📊
