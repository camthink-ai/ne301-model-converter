# NE301 模型转换器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

**零代码、端到端的 PyTorch 到 NE301 模型转换平台**

通过 Web 界面将 PyTorch 模型（YOLOv8）转换为 NE301 边缘设备的 `.bin` 格式，无需命令行专业知识。

[English](README.md) | [中文文档](README_cn.md)

---

## ✨ 核心特性

- 🎯 **零代码操作** - 基于 Web 的界面，无需 CLI 知识
- 🔄 **端到端自动化** - PyTorch → 量化 → NE301 .bin 全自动流程
- 📊 **实时反馈** - WebSocket 驱动的进度更新
- 🔧 **智能修复** - 自动诊断和修复 NE301 OOM 问题（v2.1+）
- 🎨 **校准支持** - 使用自定义数据集提高量化精度

---

## 🚀 快速开始（5 分钟）

### 前置要求

- **Docker Desktop** 已安装并运行
- **4GB+ 内存** 可用
- **10GB+ 磁盘空间**

### 一键部署

```bash
# 1. 克隆仓库
git clone https://github.com/harryhua-ai/model-converter.git
cd model-converter
git submodule update --init --recursive

# 2. 拉取 NE301 镜像
docker pull camthink/ne301-dev:latest

# 3. 启动服务
docker-compose up -d

# 4. 打开浏览器
open http://localhost:8000
```

### 第一次转换

1. 打开 http://localhost:8000
2. 上传 PyTorch 模型（`example/best.pt`）
3. 上传类别定义（`example/test.yaml`）
4. 上传校准数据集（`example/calibration.zip`）- **强烈建议**
5. 选择输入尺寸（256x256 / 320x320 / 480x480）
6. 点击"开始转换"
7. 等待 2-5 分钟 → 下载 `.bin` 文件

**完成！** 您的模型已准备好部署到 NE301。

---

## 📖 文档导航

### 快速开始
- **[快速开始指南](docs/QUICK_START_cn.md)** - 5 分钟教程（含图片）

### 部署指南
- **[Docker 部署](docs/DOCKER_DEPLOYMENT_cn.md)** - 完整 Docker 指南
  - 三种部署模式
  - 环境配置
  - 故障排查

### 开发指南
- **[开发文档](CLAUDE.md)** - 完整开发者文档

---

## 🛠️ 技术栈

**前端**: Preact 10 + TypeScript + Tailwind CSS + Vite

**后端**: Python 3.11/3.12 + FastAPI + WebSocket + Docker SDK

**ML 管道**:
- PyTorch 2.4.0（模型导出）
- Ultralytics 8.3.0（YOLO 处理）
- TensorFlow 2.16.2（TFLite 转换）
- STMicroelectronics 官方量化工具

---

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│    前端 (Preact + TypeScript)            │
└────────────────┬────────────────────────┘
                 │ HTTP/WebSocket
                 ▼
┌─────────────────────────────────────────┐
│    后端 (FastAPI + Python)               │
│  ┌──────────┐  ┌──────────┐             │
│  │ API      │  │WebSocket │             │
│  │ 路由     │  │ 管理器   │             │
│  └──────────┘  └──────────┘             │
└────────────────┬────────────────────────┘
                 │ Docker SDK
                 ▼
┌─────────────────────────────────────────┐
│    Docker 容器 (NE301 工具链)            │
│  PyTorch → TFLite → 量化 → .bin          │
└─────────────────────────────────────────┘
```

**📖 [详细架构说明](docs/ARCHITECTURE_cn.md)**

---

## 🧪 开发指南

```bash
# 后端开发
cd backend
pytest                                    # 运行测试
pytest --cov=app --cov-report=html       # 覆盖率报告

# 前端开发
cd frontend
npm run dev                               # 开发服务器
npm run build                             # 生产构建

# Docker 开发
docker-compose -f docker-compose.dev.local.yml up -d
```

**📖 [开发指南](CLAUDE.md)**

---

## 🤝 贡献指南

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

**提交规范**: 遵循 [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- STMicroelectronics - 官方 TFLite 量化工具
- Ultralytics - YOLO 模型生态

---

## 📞 联系方式

- **邮箱**: support@camthink.ai

---

**最后更新**: 2026-03-19
**版本**: 2.1.0
