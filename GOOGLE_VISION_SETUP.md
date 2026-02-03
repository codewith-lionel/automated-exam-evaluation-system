# Google Cloud Vision API Setup Guide

This system now supports **two OCR engines**:
- 🔹 **TrOCR** (Local, Free, Good for handwritten text)
- 🔹 **Google Cloud Vision** (Cloud, Powerful, Best accuracy)

## Quick Start

### Option 1: Use TrOCR (Default - No Setup Required)
The system works out of the box with TrOCR. No additional configuration needed.

### Option 2: Enable Google Cloud Vision API

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Cloud Vision API**
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

#### Step 2: Create Service Account & Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details and click "Create"
4. Grant role: "Cloud Vision AI Service Agent" or "Owner"
5. Click "Done"
6. Find your service account in the list and click on it
7. Go to "Keys" tab > "Add Key" > "Create New Key"
8. Choose JSON format and download the key file
9. Save the file securely (e.g., `google-vision-credentials.json`)

#### Step 3: Configure Your Application

**Method A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="D:\path\to\your\google-vision-credentials.json"
$env:OCR_ENGINE="google_vision"

# Windows CMD
set GOOGLE_APPLICATION_CREDENTIALS=D:\path\to\your\google-vision-credentials.json
set OCR_ENGINE=google_vision

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-vision-credentials.json"
export OCR_ENGINE=google_vision
```

**Method B: Modify config.py**
```python
# In config.py, add:
GOOGLE_VISION_CREDENTIALS = "D:/path/to/your/google-vision-credentials.json"
OCR_ENGINE = 'google_vision'
```

#### Step 4: Install Dependencies
```bash
pip install google-cloud-vision
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

#### Step 5: Run Your Application
```bash
python app.py
```

## Switching Between OCR Engines

### Via Environment Variable:
```bash
# Use Google Vision
$env:OCR_ENGINE="google_vision"

# Use TrOCR (default)
$env:OCR_ENGINE="trocr"

# Auto-detect (tries Google Vision, falls back to TrOCR)
$env:OCR_ENGINE="auto"
```

### Via Code:
```python
# In your backend/api.py or wherever you call OCR:
from backend.ocr_processor import extract_text_from_image

# Explicitly use Google Vision
text = extract_text_from_image('image.jpg', engine='google_vision')

# Explicitly use TrOCR
text = extract_text_from_image('image.jpg', engine='trocr')

# Auto-detect based on config
text = extract_text_from_image('image.jpg', engine='auto')
```

## Pricing & Free Tier

### Google Cloud Vision API Pricing:
- **Free Tier**: 1,000 units/month for text detection
- **After Free Tier**: $1.50 per 1,000 units
- 1 unit = 1 image processed

### When to Use Each Engine:

| Feature | TrOCR | Google Vision |
|---------|-------|---------------|
| **Cost** | Free | Paid (1000 free/month) |
| **Speed** | Slower | Faster |
| **Accuracy** | Good | Excellent |
| **Handwritten** | Very Good | Excellent |
| **Printed Text** | Good | Excellent |
| **Setup** | None | Requires API key |
| **Internet** | Not required | Required |
| **Best For** | Development, Low volume | Production, High accuracy |

## Troubleshooting

### Error: "Google Cloud Vision API not initialized"
- ✅ Check that `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- ✅ Verify the JSON key file exists and is valid
- ✅ Ensure the path has no spaces or use quotes

### Error: "API has not been enabled"
- ✅ Go to Google Cloud Console and enable Cloud Vision API
- ✅ Wait a few minutes for API activation

### Error: "Permission denied"
- ✅ Check service account has proper roles
- ✅ Verify billing is enabled on your project

### Still Using TrOCR When You Want Google Vision?
- ✅ Check `OCR_ENGINE` environment variable is set to "google_vision"
- ✅ Restart your application after setting environment variables
- ✅ Check console output for "Using OCR engine: google_vision"

## Architecture Flow

```
User uploads image
   ↓
Backend receives file
   ↓
Check OCR_ENGINE config
   ↓
┌────────────────┬────────────────┐
│  google_vision │     trocr      │
└────────────────┴────────────────┘
        ↓                ↓
Google Cloud API    Local Model
        ↓                ↓
   Extracted Text ← ← ← ← 
        ↓
NLP Evaluation
        ↓
Results & Feedback
```

## Example Usage

### Python Example (like shown):
```python
from google.cloud import vision
from io import BytesIO
from PIL import Image

# Initialize client
client = vision.ImageAnnotatorClient()

# Read image
with open('student_answer.jpg', 'rb') as image_file:
    content = image_file.read()

# Create image object
image = vision.Image(content=content)

# Perform text detection
response = client.text_detection(image=image)
texts = response.text_annotations

# Get full text
if texts:
    extracted_text = texts[0].description
    print(extracted_text)
```

### Node.js Example (for reference):
```javascript
const vision = require('@google-cloud/vision');
const client = new vision.ImageAnnotatorClient();

const [result] = await client.textDetection('image.jpg');
const text = result.fullTextAnnotation.text;
console.log(text);
```

## Benefits of Google Vision for Your System

✅ **Higher Accuracy**: Better text recognition, especially for:
   - Mixed printed & handwritten text
   - Low-quality scans
   - Various fonts and sizes

✅ **Faster Processing**: Cloud-based processing is typically faster

✅ **Document Understanding**: Detects text structure and layout

✅ **Language Support**: Supports 50+ languages

✅ **Handles Edge Cases**: Better with:
   - Rotated text
   - Skewed images
   - Complex layouts

## Next Steps

1. ✅ **Installed** - Google Vision package added to requirements.txt
2. ✅ **Configured** - System supports both TrOCR and Google Vision
3. ⏳ **Setup Credentials** - Follow steps above to get your API key
4. ⏳ **Test** - Upload a sample exam and compare results
5. ⏳ **Deploy** - Use Google Vision for production, TrOCR for development

Need help? Check the [Google Cloud Vision Documentation](https://cloud.google.com/vision/docs)
