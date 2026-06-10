# Docker - Smart Test Deployment

> **Status: unverified.** The Docker setup predates the v1.4.1 hardening and
> has not been built/tested since. It installs the full requirements.txt and
> may need updates (e.g. new env vars in .env.example). Treat as a starting
> point, not a guarantee.

Ejecuta Smart Test con Docker. Cero configuración local.

---

## 📋 Requisitos

- Docker instalado ([descargar](https://www.docker.com/products/docker-desktop))
- Docker Compose (incluido en Docker Desktop)

---

## 🚀 Inicio Rápido

### Opción 1: API + Ollama (Recomendado)

```bash
# Clone o descarga el repo
cd smart-web-test-ai

# Ejecuta
docker-compose --profile full up -d

# Espera a que Ollama descarguue modelos (~5-10 min primera vez)
# Verifica logs:
docker logs smart-test-ollama

# Acceso:
# API:      http://localhost:8000
# Web UI:   http://localhost:8501
# Grafana:  http://localhost:3000
# Ollama:   http://localhost:11434
```

### Opción 2: Solo API

```bash
docker-compose --profile api-only up -d
```

### Opción 3: Solo Web UI

```bash
docker-compose --profile web-only up -d
```

### Opción 4: Solo Monitoring (Grafana + InfluxDB)

```bash
docker-compose --profile monitoring up -d
```

---

## 🛑 Detener Contenedores

```bash
# Detener todo
docker-compose down

# Detener y borrar volúmenes
docker-compose down -v

# Detener servicio específico
docker-compose stop api
```

---

## 📊 Comandos Útiles

### Ver logs
```bash
# Todos
docker-compose logs -f

# Específico
docker-compose logs -f api
docker-compose logs -f ollama
docker-compose logs -f web
```

### Ver estado
```bash
docker-compose ps
```

### Ejecutar comando en contenedor
```bash
# API
docker exec smart-test-api python script.py

# Ollama
docker exec smart-test-ollama ollama list
```

### Entrar en contenedor
```bash
docker exec -it smart-test-api bash
```

### Rebuild
```bash
docker-compose build --no-cache
```

---

## 🔧 Configuración

### Variables de Entorno

Crea `.env`:
```bash
# Ollama
OLLAMA_HOST=http://ollama:11434

# Grafana
GF_SECURITY_ADMIN_PASSWORD=your_password

# InfluxDB
INFLUXDB_ADMIN_PASSWORD=your_password
```

Aplica:
```bash
docker-compose --env-file .env up -d
```

### Puertos Personalizados

Edita `docker-compose.yml`:
```yaml
api:
  ports:
    - "8000:8000"  # Cambiar primer 8000
```

---

## 📥 Descargar Modelos Ollama

Dentro del contenedor:
```bash
docker exec smart-test-ollama ollama pull mistral
docker exec smart-test-ollama ollama pull llava
```

O usar API:
```bash
curl http://localhost:11434/api/pull -d '{"name":"mistral"}'
```

---

## 🌐 Acceso Remoto

### Exponerse en red local
```bash
# docker-compose.yml
services:
  api:
    ports:
      - "0.0.0.0:8000:8000"  # Accesible desde otras máquinas
```

Acceso: `http://192.168.1.100:8000` (cambiar IP)

### Con proxy inverso (Nginx)
```nginx
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 📦 Build Personalizado

### Cambiar base image
```dockerfile
FROM python:3.11-slim  # Cambiar versión
```

### Optimizar tamaño
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
RUN pip install -r requirements.txt
FROM python:3.11-slim
COPY --from=builder /usr/local /usr/local
```

---

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Verifica que Ollama está corriendo
docker logs smart-test-ollama

# Reinicia
docker-compose restart ollama
```

### "Port already in use"
```bash
# Cambia puerto en docker-compose.yml
ports:
  - "8001:8000"  # localhost:8001 → container:8000
```

### "Out of memory"
```bash
# Aumenta Docker memory límite
# Docker Desktop → Settings → Resources → Memory
```

### "Modelo no encontrado"
```bash
# Descarga primero
docker exec smart-test-ollama ollama pull mistral

# Verifica
docker exec smart-test-ollama ollama list
```

### Permisos en volúmenes
```bash
# Fix permisos
sudo chown -R $USER:$USER .

# O usa docker con sudo
sudo docker-compose up
```

---

## 📊 Perfiles Disponibles

| Perfil | Servicios | Uso |
|--------|-----------|-----|
| `full` | Todo | Development/Testing |
| `api-only` | API + Ollama | Producción minimalista |
| `web-only` | Web + Ollama | UI development |
| `ollama-only` | Solo Ollama | Usar con cliente local |
| `monitoring` | Grafana + InfluxDB | Observabilidad |

---

## 🚀 Producción

### Health checks

```bash
# API
curl http://localhost:8000/health

# Ollama
curl http://localhost:11434/api/tags

# Todos
docker-compose ps
```

### Backup volúmenes

```bash
docker run --rm \
  -v smart-test_ollama_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/ollama.tar.gz -C /data .
```

### Restore

```bash
docker run --rm \
  -v smart-test_ollama_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/ollama.tar.gz -C /data
```

---

## 📚 Referencias

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Ollama Docs](https://ollama.ai)

---

## 🎯 Casos de Uso

### Desarrollo Local
```bash
docker-compose --profile full up -d
```

### CI/CD Pipeline
```bash
docker build -t smart-test:$VERSION .
docker push myregistry/smart-test:$VERSION
```

### Kubernetes
```bash
# Crear imagen
docker build -t smart-test:latest .

# Push a registry
docker push myregistry/smart-test:latest

# Deploy
kubectl apply -f k8s/deployment.yaml
```

---

**Docker = Una sola línea para setup completo**
