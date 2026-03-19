# NE301 Model Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

**A zero-code, end-to-end PyTorch-to-NE301 model conversion platform**

Convert PyTorch models (YOLOv8) to NE301 edge device `.bin` format through a web interface. No CLI expertise required.

[English](README.md) | [中文文档](README_cn.md)

---

## ✨ Key Features

- 🎯 **Zero-Code Operation** - Web-based UI, no CLI knowledge needed
- 🔄 **End-to-End Automation** - PyTorch → Quantization → NE301 .bin in one flow
- 📊 **Real-Time Feedback** - WebSocket-powered progress updates
- 🔧 **Smart Fixes** - Auto-diagnose and fix NE301 OOM issues (v2.1+)
- 🎨 **Calibration Support** - Improve quantization accuracy with custom datasets

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Docker Desktop** installed and running
- **4GB+ RAM** available
- **10GB+ disk space**

### One-Command Deployment

```bash
# 1. Clone the repository
git clone https://github.com/harryhua-ai/model-converter.git
cd model-converter
git submodule update --init --recursive

# 2. Pull NE301 image
docker pull camthink/ne301-dev:latest

# 3. Start services
docker-compose up -d

# 4. Open browser
open http://localhost:8000
```

### First Conversion

1. Open http://localhost:8000
2. Upload PyTorch model (`example/best.pt`)
3. Upload class definition (`example/test.yaml`)
4. Upload calibration dataset (`example/calibration.zip`) - **strongly recommended**
5. Select input size (256x256 / 320x320 / 480x480)
6. Click "Start Conversion"
7. Wait 2-5 minutes → Download `.bin` file

**Done!** Your model is ready for NE301 deployment.

---

## 📖 Documentation

### Getting Started
- **[Quick Start Guide](docs/QUICK_START.md)** - 5-minute tutorial with images

### Deployment
- **[Docker Deployment](docs/DOCKER_DEPLOYMENT.md)** - Complete Docker guide
  - Three deployment modes
  - Environment configuration
  - Troubleshooting

### Development
- **[Development Guide](CLAUDE.md)** - Complete developer documentation

---

## 🛠️ Technology Stack

**Frontend**: Preact 10 + TypeScript + Tailwind CSS + Vite

**Backend**: Python 3.11/3.12 + FastAPI + WebSocket + Docker SDK

**ML Pipeline**:
- PyTorch 2.4.0 (model export)
- Ultralytics 8.3.0 (YOLO processing)
- TensorFlow 2.16.2 (TFLite conversion)
- STMicroelectronics official quantization

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│    Frontend (Preact + TypeScript)        │
└────────────────┬────────────────────────┘
                 │ HTTP/WebSocket
                 ▼
┌─────────────────────────────────────────┐
│    Backend (FastAPI + Python)            │
│  ┌──────────┐  ┌──────────┐             │
│  │ API      │  │WebSocket │             │
│  │ Router   │  │ Manager  │             │
│  └──────────┘  └──────────┘             │
└────────────────┬────────────────────────┘
                 │ Docker SDK
                 ▼
┌─────────────────────────────────────────┐
│    Docker Container (NE301 Tools)        │
│  PyTorch → TFLite → Quantization → .bin  │
└─────────────────────────────────────────┘
```

**📖 [Detailed Architecture](docs/ARCHITECTURE.md)**

---

## 🧪 Development

```bash
# Backend development
cd backend
pytest                                    # Run tests
pytest --cov=app --cov-report=html       # Coverage report

# Frontend development
cd frontend
npm run dev                               # Dev server
npm run build                             # Production build

# Docker development
docker-compose -f docker-compose.dev.local.yml up -d
```

**📖 [Development Guide](CLAUDE.md)**

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

**Commit Convention**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- STMicroelectronics - Official TFLite quantization tools
- Ultralytics - YOLO model ecosystem

---

## 📞 Contact

- **Email**: support@camthink.ai

---

**Last Updated**: 2026-03-19
**Version**: 2.1.0
