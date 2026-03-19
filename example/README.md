# Example Files

This directory contains sample files for testing the NE301 Model Converter.

---

## 📂 Files

### 1. `best.pt` (6MB)

**YOLOv8 Model** - 30-class household items detection model

- **Type**: PyTorch model (`.pt`)
- **Size**: 6.0 MB
- **Classes**: 30 categories (household items)
- **Input Size**: 640x640 (default)
- **Use Case**: Test model conversion pipeline

**Model Details**:
- Trained on household trash/recycling dataset
- Detects common household items (fruits, vegetables, food, packaging, etc.)
- Suitable for edge deployment

### 2. `test.yaml` (531B)

**Class Definitions** - YAML file with class names

```yaml
names:
- Banana
- Apple
- Orange
- Tomato
- Carrot
- Cucumber
- Potato
- Bread
- Cake
- Pizza
- Hamburger
- Chicken
- Fish
- Food
- Tin can
- Bottle
- Facial tissue holder
- Toilet paper
- Paper towel
- Milk
- Snack
- Plastic bag
- Candy
- Light bulb
- Toothbrush
- Soap dispenser
- Drinking straw
- Fast food
- Pasta
- Pastry
nc: 30
```

**Usage**:
- Upload to the web interface
- Used for setting number of classes in model config
- Display class names in detection results

### 3. `calibration.zip` (10MB)

**Calibration Dataset** - Sample images for quantization

- **Format**: ZIP archive
- **Size**: 10 MB
- **Contents**: ~50 representative images
- **Image Formats**: `.jpg`, `.png`
- **Purpose**: Improve quantization accuracy

**Why Calibration?**:
- ✅ Improves INT8 quantization accuracy by 5-15%
- ✅ Helps model adapt to real-world data distribution
- ✅ Recommended for production deployment

---

## 🚀 Quick Test

### Option 1: Web Interface

1. Start the service:
   ```bash
   cd ..
   docker-compose up -d
   ```

2. Open http://localhost:8000

3. Upload files:
   - Model: `example/best.pt`
   - Classes: `example/test.yaml`
   - Calibration: `example/calibration.zip`

4. Select input size (256x256 recommended)

5. Click "Start Conversion"

6. Wait 2-5 minutes → Download `.bin` file

### Option 2: API

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "model=@example/best.pt" \
  -F "yaml_file=@example/test.yaml" \
  -F "calibration_dataset=@example/calibration.zip" \
  -F 'config={"input_size": 256, "model_type": "yolov8"}'
```

---

## 📊 Expected Results

### Conversion Output

- **Output File**: `best_ne301.bin` (~4-5 MB)
- **Conversion Time**: 2-3 minutes (256x256)
- **Model Size Reduction**: ~15-20% smaller than original

### Model Performance

| Input Size | FPS (NE301) | Accuracy | Memory |
|-----------|-------------|----------|--------|
| 256x256 | 30+ | ⭐⭐ | Low |
| 320x320 | 20-30 | ⭐⭐⭐ | Medium |
| 480x480 | 10-20 | ⭐⭐⭐⭐ | High |

---

## 🔧 Model Details

### Architecture

- **Base Model**: YOLOv8
- **Backbone**: CSPDarknet53
- **Neck**: PANet
- **Head**: Decoupled Head
- **Classes**: 30 household items

### Training Dataset

- **Source**: Household Trash/Recycling Dataset
- **Categories**: 30 classes
- **Use Case**: Smart waste sorting, inventory management

---

## 💡 Usage Tips

### 1. Input Size Selection

- **256x256**: Fastest, best for real-time (30+ FPS)
- **320x320**: Balanced speed and accuracy
- **480x480**: Highest accuracy, slower (10-20 FPS)

### 2. Calibration Dataset

- Use 50-100 representative images
- Images should match deployment scenario
- Covers different lighting/angles/conditions

### 3. Class Definitions

- Ensure class names match your use case
- Number of classes (`nc`) must match model
- YAML format required

---

## 🎯 Use Cases

This example model is suitable for:

1. **Smart Waste Sorting**
   - Recyclable vs non-recyclable classification
   - Automated trash bin systems

2. **Inventory Management**
   - Retail shelf monitoring
   - Warehouse item detection

3. **Smart Home**
   - Fridge inventory
   - Kitchen assistant

4. **Educational**
   - Learning model conversion
   - Testing NE301 deployment

---

## 📚 Related Documentation

- [Quick Start Guide](../docs/QUICK_START.md)
- [Docker Deployment](../docs/DOCKER_DEPLOYMENT.md)
- [Full Documentation](../CLAUDE.md)

---

## ⚠️ Notes

- This model is for **testing purposes only**
- For production use, train on your own dataset
- Calibration dataset quality affects quantization accuracy
- Input size impacts both speed and accuracy

---

## 🔄 Generate Your Own

### Custom Model

```bash
# Train your own YOLOv8 model
yolo detect train data=your_data.yaml model=yolov8n.pt epochs=100

# Export to PyTorch format
yolo export model=best.pt format=pytorch
```

### Custom Classes

```yaml
# your_classes.yaml
names:
  - your_class_1
  - your_class_2
  # ...
nc: <number_of_classes>
```

### Custom Calibration

```bash
# Collect representative images
mkdir calibration_images
# Add 50-100 images from your deployment scenario

# Create ZIP
zip -r calibration.zip calibration_images/
```

---

**Last Updated**: 2026-03-19
