# Docker 部署指南 - NE301 模型转换器

**基于 Docker 的完整部署指南**

本指南涵盖使用 Docker 部署 NE301 模型转换器的所有方面，从本地开发到生产环境。

---

## 📋 前置要求

- **Docker Desktop** 已安装并运行
- **4GB+ 内存** 可用于 Docker
- **10GB+ 磁盘空间** 用于 Docker 镜像
- **网络连接**（首次下载镜像需要）

---

## 🚀 快速开始

### 一键部署

```bash
# 1. 拉取 NE301 依赖镜像
docker pull camthink/ne301-dev:latest

# 2. 构建并启动服务
docker-compose up -d

# 3. 访问 Web 界面
# 打开浏览器访问 http://localhost:8000
```

**部署完成！** 现在可以开始转换模型。

---

## 📊 Docker Compose 配置选项

本项目提供三种 Docker Compose 配置，适用于不同场景：

| 文件 | 用途 | 启动速度 | 使用场景 |
|------|------|---------|---------|
| `docker-compose.yml` | **生产环境** | ~2 分钟 | 生产部署、首次部署 |
| `docker-compose.dev.yml` | 开发环境 | ~2 分钟 | 搭建开发环境 |
| `docker-compose.dev.local.yml` | **本地开发** | ~5 秒 | 日常开发（推荐）|

### 生产环境部署（推荐）

```bash
# 使用生产配置构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**特点**:
- 前端和后端集成在单个镜像中
- 代码构建到镜像中（无卷挂载）
- 针对生产性能优化
- 适合云部署

### 本地开发（最快）

```bash
# 首次构建
docker-compose build

# 使用本地开发配置启动（~5 秒）
docker-compose -f docker-compose.dev.local.yml up -d

# 代码修改自动重载（~2 秒）
# Python 代码修改无需重新构建

# 查看日志
docker-compose -f docker-compose.dev.local.yml logs -f
```

**特点**:
- Python 代码以卷形式挂载
- 修改后 ~2 秒生效（只需重启）
- 前端预构建到镜像中
- 最适合日常开发

---

## 🔄 何时需要重建 Docker 镜像

### 无需重建（代码挂载模式）

使用 `docker-compose.dev.local.yml` 时：
- ✅ 修改 `backend/app/` Python 文件
- ✅ 修改 `backend/tools/` 脚本

**解决方案**：只需重启容器
```bash
docker-compose -f docker-compose.dev.local.yml restart api
```

### 必须重建镜像

以下情况必须重建镜像：

1. **修改 `requirements.txt`**
   ```bash
   docker-compose build --no-cache api
   ```

2. **修改前端代码** (`frontend/`)
   ```bash
   docker-compose build --no-cache api
   ```

3. **修改 `Dockerfile`**
   ```bash
   docker-compose build --no-cache api
   ```

---

## ⚙️ 环境变量

创建 `backend/.env` 文件（可选）：

```env
# Docker 配置
NE301_DOCKER_IMAGE=camthink/ne301-dev:latest
NE301_PROJECT_PATH=/app/ne301

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=False

# 日志级别
LOG_LEVEL=INFO

# 文件路径
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
OUTPUT_DIR=./outputs
MAX_UPLOAD_SIZE=524288000  # 500MB
```

### 配置说明

| 变量 | 描述 | 默认值 | 示例 |
|------|------|--------|------|
| `NE301_DOCKER_IMAGE` | NE301 Docker 镜像名称 | `camthink/ne301-dev:latest` | 自定义镜像 |
| `NE301_PROJECT_PATH` | 容器内 NE301 项目路径 | `/app/ne301` | `/opt/ne301` |
| `HOST` | 服务器主机 | `0.0.0.0` | `127.0.0.1` |
| `PORT` | 服务器端口 | `8000` | `3000` |
| `DEBUG` | 启用调试模式 | `False` | `True` |
| `LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG`, `WARNING`, `ERROR` |
| `MAX_UPLOAD_SIZE` | 最大上传文件大小（字节） | `524288000` (500MB) | `1048576000` (1GB) |

---

## 🛠️ 常用命令

### 服务管理

```bash
# 查看状态
docker-compose ps

# 查看日志（实时）
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器 + 卷
docker-compose down -v
```

### 容器操作

```bash
# 进入容器 shell
docker-compose exec api /bin/bash

# 检查容器健康状态
docker inspect --format='{{.State.Health.Status}}' model-converter-api

# 查看资源使用情况
docker stats model-converter-api
```

### 镜像管理

```bash
# 构建镜像
docker-compose build

# 强制重建（无缓存）
docker-compose build --no-cache

# 查看镜像
docker images | grep model-converter

# 删除旧镜像
docker image prune -f
```

---

## 📊 性能对比

| 操作 | 代码挂载模式 | 镜像内置模式 |
|------|------------|-------------|
| 代码修改生效 | ~2 秒（重启） | ~5-10 分钟（重建） |
| 镜像大小 | 1.01 GB | 1.01 GB |
| 适用场景 | 开发调试 | 生产部署 |
| 依赖修改 | 需要重建 | 需要重建 |
| 前端修改 | 需要重建 | 需要重建 |
| 启动时间 | ~5 秒 | ~2 分钟 |
| 资源占用 | 较低（共享代码） | 较高（全部在镜像） |

---

## 🏗️ 架构说明

### 单容器部署

```
┌─────────────────────────────────────────┐
│    Docker 容器 (API + 前端)              │
│  ┌──────────┐         ┌──────────┐      │
│  │  前端    │─────▶   │  后端    │      │
│  │ (dist/)  │         │(FastAPI) │      │
│  └──────────┘         └──────────┘      │
│                              │          │
│                              ▼          │
│                    Docker 适配器        │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     Docker 容器 (NE301 工具链)           │
│  PyTorch → TFLite → NE301 .bin           │
└─────────────────────────────────────────┘
```

### 多阶段构建

Dockerfile 使用多阶段构建进行优化：

- **阶段 1**: `node:20-slim` - 使用 Vite 构建前端
- **阶段 2**: `python:3.10-slim` - 使用 FastAPI 运行后端

**优势**:
- 更小的最终镜像（1.01 GB）
- 分离构建和运行时依赖
- 生产环境部署更快

---

## 🌟 最佳实践

### 1. 日常开发

使用本地开发配置实现最快迭代：

```bash
docker-compose -f docker-compose.dev.local.yml up -d
```

**优势**:
- 代码修改 ~2 秒生效
- Python 代码无需重建
- 理想用于调试和测试

### 2. 依赖修改后重建

修改 `requirements.txt` 或前端代码时：

```bash
docker-compose build
```

### 3. 生产部署

使用生产配置进行部署：

```bash
docker-compose up -d
```

**优势**:
- 所有代码构建到镜像中
- 无卷挂载开销
- 针对性能优化

### 4. 定期清理

清理未使用的资源：

```bash
# 停止并删除容器
docker-compose down

# 删除未使用的 Docker 资源
docker system prune -f

# 删除旧镜像
docker image prune -f
```

---

## 🐛 故障排查

### Docker 未运行

**错误**: `Cannot connect to the Docker daemon`

**解决方案**:
1. 启动 Docker Desktop
2. 验证：`docker ps`

### 镜像拉取失败

**错误**: `failed to resolve reference`

**解决方案**:
1. 检查网络连接
2. 如需要，配置 Docker 镜像加速器
3. 手动拉取：`docker pull camthink/ne301-dev:latest`

### 端口已被占用

**错误**: `port is already allocated`

**解决方案**:
```bash
# 查找占用端口 8000 的进程
lsof -i :8000

# 停止旧容器
docker-compose down

# 重启
docker-compose up -d
```

### 内存不足

**错误**: `OCI runtime create failed`

**解决方案**:
```bash
# 使用资源占用较低的本地开发配置
docker-compose -f docker-compose.dev.local.yml up -d

# 或在 Docker Desktop 设置中增加内存限制
```

### 代码修改未生效

**症状**: 修改了 Python 代码但未反映

**解决方案**:
```bash
# 方案 1: 重启容器（代码挂载模式）
docker-compose -f docker-compose.dev.local.yml restart api

# 方案 2: 使用开发配置（推荐）
docker-compose -f docker-compose.dev.local.yml up -d
```

### 容器健康检查失败

**错误**: 容器显示为 "unhealthy"

**解决方案**:
```bash
# 检查容器日志
docker-compose logs api

# 检查健康检查状态
docker inspect --format='{{json .State.Health}}' model-converter-api | jq

# 重启容器
docker-compose restart api
```

---

## 📚 其他资源

- **[快速开始指南](QUICK_START_cn.md)** - 5 分钟教程
- **[用户指南](USER_GUIDE_cn.md)** - 完整功能说明
- **[架构概览](ARCHITECTURE_cn.md)** - 系统设计
- **[故障排查](TROUBLESHOOTING_cn.md)** - 完整故障排查指南

---

## 🆘 需要帮助？

- **问题反馈**: [GitHub Issues](https://github.com/harryhua-ai/model-converter/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/harryhua-ai/model-converter/discussions)
- **文档**: [完整文档](../CLAUDE.md)

---

**最后更新**: 2026-03-19
**文档版本**: 2.0
