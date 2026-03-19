# Docker Deployment Guide - NE301 Model Converter

**Complete guide for Docker-based deployment**

This guide covers all aspects of deploying NE301 Model Converter using Docker, from local development to production.

---

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **4GB+ RAM** available for Docker
- **10GB+ disk space** for Docker images
- **Internet connection** (for first-time image download)

---

## 🚀 Quick Start

### One-Command Deployment

```bash
# 1. Pull NE301 dependency image
docker pull camthink/ne301-dev:latest

# 2. Build and start the service
docker-compose up -d

# 3. Access the web interface
# Open http://localhost:8000 in your browser
```

**Deployment complete!** You can now start converting models.

---

## 📊 Docker Compose Configuration Options

This project provides three Docker Compose configurations for different scenarios:

| File | Purpose | Startup Speed | Use Case |
|------|---------|---------------|----------|
| `docker-compose.yml` | **Production** | ~2 min | Production deployment, first-time setup |
| `docker-compose.dev.yml` | Development | ~2 min | Development environment setup |
| `docker-compose.dev.local.yml` | **Local Development** | ~5 sec | Daily development (recommended) |

### Production Deployment (Recommended)

```bash
# Build and start with production configuration
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

**Features**:
- Frontend and backend integrated in single image
- Code built into image (no volume mounts)
- Optimized for production performance
- Suitable for cloud deployment

### Local Development (Fastest)

```bash
# First-time build
docker-compose build

# Start with local development config (~5 sec)
docker-compose -f docker-compose.dev.local.yml up -d

# Code changes auto-reload (~2 sec)
# No need to rebuild for Python code changes

# View logs
docker-compose -f docker-compose.dev.local.yml logs -f
```

**Features**:
- Python code mounted as volumes
- Changes take effect in ~2 seconds (just restart)
- Frontend pre-built into image
- Best for daily development

---

## 🔄 When to Rebuild Docker Images

### No Rebuild Needed (Code Mount Mode)

When using `docker-compose.dev.local.yml`:
- ✅ Modified `backend/app/` Python files
- ✅ Modified `backend/tools/` scripts

**Solution**: Just restart the container
```bash
docker-compose -f docker-compose.dev.local.yml restart api
```

### Rebuild Required

You MUST rebuild the image when:

1. **Modified `requirements.txt`**
   ```bash
   docker-compose build --no-cache api
   ```

2. **Modified frontend code** (`frontend/`)
   ```bash
   docker-compose build --no-cache api
   ```

3. **Modified `Dockerfile`**
   ```bash
   docker-compose build --no-cache api
   ```

---

## ⚙️ Environment Variables

Create `backend/.env` file (optional):

```env
# Docker Configuration
NE301_DOCKER_IMAGE=camthink/ne301-dev:latest
NE301_PROJECT_PATH=/app/ne301

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Log Level
LOG_LEVEL=INFO

# File Paths
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
OUTPUT_DIR=./outputs
MAX_UPLOAD_SIZE=524288000  # 500MB
```

### Configuration Explanation

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `NE301_DOCKER_IMAGE` | NE301 Docker image name | `camthink/ne301-dev:latest` | Custom registry image |
| `NE301_PROJECT_PATH` | NE301 project path in container | `/app/ne301` | `/opt/ne301` |
| `HOST` | Server host | `0.0.0.0` | `127.0.0.1` |
| `PORT` | Server port | `8000` | `3000` |
| `DEBUG` | Enable debug mode | `False` | `True` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `WARNING`, `ERROR` |
| `MAX_UPLOAD_SIZE` | Max upload file size (bytes) | `524288000` (500MB) | `1048576000` (1GB) |

---

## 🛠️ Common Commands

### Service Management

```bash
# View status
docker-compose ps

# View logs (real-time)
docker-compose logs -f

# Restart service
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

### Container Operations

```bash
# Enter container shell
docker-compose exec api /bin/bash

# Check container health
docker inspect --format='{{.State.Health.Status}}' model-converter-api

# View resource usage
docker stats model-converter-api
```

### Image Management

```bash
# Build image
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache

# View images
docker images | grep model-converter

# Remove old images
docker image prune -f
```

---

## 📊 Performance Comparison

| Operation | Code Mount Mode | Image Built-in Mode |
|-----------|----------------|---------------------|
| Code changes take effect | ~2 sec (restart) | ~5-10 min (rebuild) |
| Image size | 1.01 GB | 1.01 GB |
| Use case | Development | Production |
| Dependency changes | Rebuild required | Rebuild required |
| Frontend changes | Rebuild required | Rebuild required |
| Startup time | ~5 sec | ~2 min |
| Resource usage | Lower (shared code) | Higher (all in image) |

---

## 🏗️ Architecture

### Single-Container Deployment

```
┌─────────────────────────────────────────┐
│    Docker Container (API + Frontend)     │
│  ┌──────────┐         ┌──────────┐      │
│  │ Frontend │─────▶   │ Backend  │      │
│  │ (dist/)  │         │ (FastAPI)│      │
│  └──────────┘         └──────────┘      │
│                              │          │
│                              ▼          │
│                    Docker Adapter       │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     Docker Container (NE301 Tools)       │
│  PyTorch → TFLite → NE301 .bin           │
└─────────────────────────────────────────┘
```

### Multi-Stage Build

The Dockerfile uses multi-stage build for optimization:

- **Stage 1**: `node:20-slim` - Build frontend with Vite
- **Stage 2**: `python:3.10-slim` - Run backend with FastAPI

**Benefits**:
- Smaller final image (1.01 GB)
- Separate build and runtime dependencies
- Faster deployment in production

---

## 🌟 Best Practices

### 1. Daily Development

Use local development configuration for fastest iteration:

```bash
docker-compose -f docker-compose.dev.local.yml up -d
```

**Benefits**:
- Code changes in ~2 seconds
- No rebuild needed for Python code
- Ideal for debugging and testing

### 2. Rebuild After Dependency Changes

When you modify `requirements.txt` or frontend code:

```bash
docker-compose build
```

### 3. Production Deployment

Use production configuration for deployment:

```bash
docker-compose up -d
```

**Benefits**:
- All code built into image
- No volume mount overhead
- Optimized for performance

### 4. Regular Cleanup

Clean up unused resources:

```bash
# Stop and remove containers
docker-compose down

# Remove unused Docker resources
docker system prune -f

# Remove old images
docker image prune -f
```

---

## 🐛 Troubleshooting

### Docker Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solution**:
1. Start Docker Desktop
2. Verify: `docker ps`

### Image Pull Failed

**Error**: `failed to resolve reference`

**Solution**:
1. Check network connection
2. Configure Docker mirror if needed
3. Manually pull: `docker pull camthink/ne301-dev:latest`

### Port Already In Use

**Error**: `port is already allocated`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Stop old containers
docker-compose down

# Restart
docker-compose up -d
```

### Out of Memory

**Error**: `OCI runtime create failed`

**Solution**:
```bash
# Use local dev config with lower resource usage
docker-compose -f docker-compose.dev.local.yml up -d

# Or increase Docker memory limit in Docker Desktop settings
```

### Code Changes Not Taking Effect

**Symptom**: Modified Python code but changes not reflected

**Solution**:
```bash
# Option 1: Restart container (for code mount mode)
docker-compose -f docker-compose.dev.local.yml restart api

# Option 2: Use development config (recommended)
docker-compose -f docker-compose.dev.local.yml up -d
```

### Container Health Check Failed

**Error**: Container shows as "unhealthy"

**Solution**:
```bash
# Check container logs
docker-compose logs api

# Check health check status
docker inspect --format='{{json .State.Health}}' model-converter-api | jq

# Restart container
docker-compose restart api
```

---

## 📚 Additional Resources

- **[Docker Compose Guide](DOCKER_COMPOSE_GUIDE.md)** - Detailed configuration options
- **[Local Development Guide](DOCKER_DEVELOPMENT_GUIDE.md)** - Development setup
- **[Troubleshooting](TROUBLESHOOTING.md)** - Complete troubleshooting guide

---

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/harryhua-ai/model-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/harryhua-ai/model-converter/discussions)
- **Documentation**: [Full Documentation](../CLAUDE.md)

---

**Last Updated**: 2026-03-19
**Document Version**: 2.0
