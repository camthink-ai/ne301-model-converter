# Quick Start Guide - NE301 Model Converter

**5-minute tutorial to convert your first model**

This guide will walk you through converting a PyTorch model to NE301 `.bin` format using our web interface.

---

## 📋 Prerequisites

Before you start, ensure you have:

- ✅ **Docker Desktop** installed and running
- ✅ **4GB+ RAM** available
- ✅ **10GB+ disk space**
- ✅ **Internet connection** (for pulling Docker images)

---

## 🚀 Step 1: Start the Service

### 1.1 Pull NE301 Docker Image

```bash
docker pull camthink/ne301-dev:latest
```

This will download the NE301 toolchain (~3GB). It may take 5-10 minutes depending on your internet speed.

### 1.2 Start the Converter Service

```bash
# Clone the repository
git clone https://github.com/harryhua-ai/model-converter.git
cd model-converter
git submodule update --init --recursive

# Start services
docker-compose up -d
```

Wait for the service to start (~2 minutes). You'll see:

```
✔ Container model-converter-api  Started
```

### 1.3 Access the Web Interface

Open your browser and navigate to:

```
http://localhost:8000
```

You should see the NE301 Model Converter interface:

![Access Web Page](images/access-web-page.png)

---

## 📦 Step 2: Upload Model and Configuration

### 2.1 Upload PyTorch Model

Click on **"Upload Model"** area and select your PyTorch model file:

- Supported formats: `.pt`, `.pth`, `.onnx`
- Maximum size: 500MB
- Example: `example/best.pt` (6MB YOLOv8 model)

![Upload PyTorch Model](images/upload-pytorch-model.png)

### 2.2 Upload Class Definition (YAML)

Upload your YAML file containing class definitions:

```yaml
# Example: example/test.yaml (30-class household items)
names:
  - Banana
  - Apple
  - Orange
  - Tomato
  # ... 30 classes total
```

![Upload Class Definition](images/upload-class.png)

### 2.3 Upload Calibration Dataset

**Upload calibration dataset (strongly recommended)**:

- **Format**: ZIP file containing images
- **Images**: 32-100 representative images
- **Formats**: `.jpg`, `.png`
- **Example**: `example/calibration.zip` (10MB, ~50 images)

![Upload Calibration Dataset](images/upload-calibration.png)

**Why calibration?**
- Improves quantization accuracy by 5-15%
- Uses real data distribution for optimization
- **Strongly recommended** for production models

---

## ⚙️ Step 3: Configure Conversion

### 3.1 Select Preset

Choose a conversion preset based on your needs:

| Preset | Input Size | Speed | Accuracy | Use Case |
|--------|-----------|-------|----------|----------|
| **Fast** | 256x256 | ⚡⚡⚡ | ⭐⭐ | Real-time detection (default) |
| **Balanced** | 320x320 | ⚡⚡ | ⭐⭐⭐ | General purpose |
| **High-Precision** | 480x480 | ⚡ | ⭐⭐⭐⭐ | Accuracy-critical |

### 3.2 Start Conversion

Click the **"Start Conversion"** button:

![Start Converter](images/start-converter.png)

---

## ✅ Step 4: Download and Deploy to NE301

Once conversion completes (typically 2-5 minutes):

![Conversion Complete](images/convert-complete.png)

### 4.1 Download .bin File

Click **"Download .bin"** to get your NE301-compatible model.

### 4.2 Deploy to NE301 Device

**Upload the `.bin` file to NE301 web interface:**

1. Access NE301 device web interface
2. Navigate to model upload section
3. Select the downloaded `.bin` file
4. Upload and wait for verification

**Verify the model loads correctly:**

![Model Verification in NE301](images/model-verification-in-ne301.png)

**Success indicators:**
- ✅ Model loads without OOM errors
- ✅ Inference runs successfully
- ✅ Output matches expected results

---

## 🎉 Congratulations!

You've successfully converted your first PyTorch model to NE301 format!

### What's Next?

- 📖 **[API Reference](API_REFERENCE.md)** - Use programmatically
- 🔧 **[Troubleshooting](TROUBLESHOOTING.md)** - Solve common issues
- 🏗️ **[Architecture](ARCHITECTURE.md)** - Understand the pipeline
- 🐳 **[Docker Deployment](DOCKER_DEPLOYMENT.md)** - Advanced configuration

---

## 🐛 Common Issues

### Issue: Docker not running

**Symptom**: `Cannot connect to the Docker daemon`

**Solution**:
```bash
# Start Docker Desktop
open -a Docker

# Verify
docker ps
```

### Issue: Port 8000 already in use

**Symptom**: `port is already allocated`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Stop old containers
docker-compose down

# Restart
docker-compose up -d
```

### Issue: Conversion failed

**Symptom**: Progress stuck or error message

**Solution**:
1. Check logs: `docker-compose logs -f`
2. Verify model format (must be `.pt` or `.pth`)
3. Ensure YAML file is valid
4. Try without calibration dataset first

**📖 [Full Troubleshooting Guide](TROUBLESHOOTING.md)**

---

## 📚 Sample Files

Use the example files provided in the repository:

```bash
# Example files in the example/ directory:
example/
├── best.pt           # 6MB YOLOv8 model (30-class household items)
├── test.yaml         # Class definitions (30 categories)
└── calibration.zip   # Calibration dataset (10MB, ~50 images)

# Or download a sample YOLOv8 model
wget https://github.com/ultralytics/assets/raw/main/yolov8n.pt
```

---

## 💡 Pro Tips

### Tip 1: Use Calibration Dataset
- Improves accuracy by 5-15%
- Use representative images from your use case
- 50-100 images is optimal

### Tip 2: Choose Right Preset
- **Fast (256x256)**: Real-time applications (30+ FPS) - default
- **Balanced (320x320)**: General purpose (20-30 FPS)
- **High-Precision (480x480)**: Accuracy-critical (10-20 FPS)

### Tip 3: Monitor Resources
```bash
# Check container resource usage
docker stats model-converter-api
```

### Tip 4: Keep Logs
```bash
# Save logs for troubleshooting
docker-compose logs > conversion.log
```

---

## 🆘 Need Help?

- **Email**: support@camthink.ai
- **Documentation**: [Full Documentation](../CLAUDE.md)

---

**Last Updated**: 2026-03-19
