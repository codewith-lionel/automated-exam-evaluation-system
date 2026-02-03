# Architecture Diagram: Dual OCR Engine System

## System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                    (Web Browser / App)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Upload Exam Image
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                        FLASK SERVER                          │
│                       (app.py + API)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Process Upload
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    OCR PROCESSOR MODULE                      │
│               (backend/ocr_processor.py)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Check OCR_ENGINE Configuration                     │  │
│  │   (from config.py or environment variable)           │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│      ┌────────┴────────┐                                    │
│      │                 │                                    │
│      ▼                 ▼                                    │
│  ┌─────────┐      ┌──────────────┐                         │
│  │  TrOCR  │      │ Google Vision│                         │
│  │ (Local) │      │    (Cloud)   │                         │
│  └────┬────┘      └──────┬───────┘                         │
│       │                  │                                  │
│       │ Microsoft        │ Google Cloud                     │
│       │ Transformer      │ Vision API                       │
│       │ Model            │ REST Call                        │
│       │                  │                                  │
│       ▼                  ▼                                  │
│  ┌─────────────────────────────┐                            │
│  │   Extracted Text (String)   │                            │
│  │   + OCR Confidence          │                            │
│  └──────────┬──────────────────┘                            │
└─────────────┼────────────────────────────────────────────────┘
              │
              │ Clean & Normalize Text
              ▼
┌─────────────────────────────────────────────────────────────┐
│                     NLP EVALUATOR MODULE                     │
│                (backend/nlp_evaluator.py)                    │
│                                                              │
│  • Compare with model answers                               │
│  • Calculate similarity scores                              │
│  • Generate feedback                                        │
│  • Assign marks                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Evaluation Results
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      RESULTS DISPLAY                         │
│                                                              │
│  • Marks awarded                                            │
│  • Detailed feedback                                        │
│  • Strengths & improvements                                 │
│  • PDF report generation                                    │
└─────────────────────────────────────────────────────────────┘
```

## OCR Engine Comparison

```
┌──────────────────────────────────────────────────────────────┐
│                          TrOCR                               │
├──────────────────────────────────────────────────────────────┤
│  Type:         Local Deep Learning Model                     │
│  Provider:     Microsoft (Hugging Face)                      │
│  Model:        microsoft/trocr-base-handwritten             │
│  Processing:   Locally on your machine (CPU/GPU)            │
│  Internet:     ❌ Not required                               │
│  Setup:        ✅ Works out of the box                       │
│  Cost:         ✅ 100% Free                                  │
│  Speed:        ⚡ Moderate (depends on hardware)            │
│  Accuracy:     ⭐⭐⭐⭐ Very Good                             │
│  Best For:     • Development & Testing                       │
│                • Handwritten text                            │
│                • Privacy-sensitive documents                 │
│                • Offline environments                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    Google Cloud Vision                       │
├──────────────────────────────────────────────────────────────┤
│  Type:         Cloud-based AI Service                        │
│  Provider:     Google Cloud Platform                         │
│  API:          Vision AI - Text Detection                    │
│  Processing:   Google's data centers                         │
│  Internet:     ✅ Required                                   │
│  Setup:        ⚙️  API key configuration needed             │
│  Cost:         💰 Free tier: 1000/month, then $1.50/1000    │
│  Speed:        ⚡⚡⚡ Very Fast                               │
│  Accuracy:     ⭐⭐⭐⭐⭐ Excellent                            │
│  Best For:     • Production environments                     │
│                • Mixed printed & handwritten                 │
│                • High-accuracy requirements                  │
│                • Poor quality scans                          │
│                • Multi-language support                      │
└──────────────────────────────────────────────────────────────┘
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Startup                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Load Configuration    │
            │  (config.py)           │
            └──────────┬─────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ OCR_ENGINE       │    │ GOOGLE_          │
│ Environment Var  │    │ APPLICATION_     │
│ or default       │    │ CREDENTIALS      │
└──────┬───────────┘    └────────┬─────────┘
       │                         │
       │ = 'trocr'               │ = 'path/to/key.json'
       │   'google_vision'       │   (if using Google)
       │   'auto'                │
       │                         │
       └──────────┬──────────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │  Initialize OCR      │
       │  Engines             │
       └──────────┬───────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌─────────────┐    ┌─────────────────┐
│ Load TrOCR  │    │ Init Google     │
│ Model       │    │ Vision Client   │
│             │    │ (if configured) │
└─────────────┘    └─────────────────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Ready to      │
         │  Process       │
         └────────────────┘
```

## Request Processing Flow

```
┌──────────────────────────────────────────────────────────────┐
│  extract_text_from_image(image_path, engine='auto')          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Determine Engine │
              │                  │
              │ if auto:         │
              │   use config     │
              └─────────┬────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
┌───────────────────┐    ┌──────────────────────┐
│ engine = 'trocr'  │    │ engine =             │
│                   │    │ 'google_vision'      │
└─────────┬─────────┘    └──────────┬───────────┘
          │                         │
          ▼                         ▼
┌───────────────────┐    ┌──────────────────────┐
│extract_text_trocr │    │extract_text_google   │
│                   │    │_vision               │
│• Preprocess       │    │                      │
│• Split to lines   │    │• Read image bytes    │
│• Process with     │    │• Call Vision API     │
│  transformer      │    │• Parse response      │
│• Merge results    │    │• Extract text        │
└─────────┬─────────┘    └──────────┬───────────┘
          │                         │
          └───────────┬─────────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ clean_ocr_text()    │
           │                     │
           │ • Remove artifacts  │
           │ • Fix common errors │
           │ • Normalize spacing │
           └──────────┬──────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ Return Extracted │
            │ Text (String)    │
            └──────────────────┘
```

## File Structure

```
automated-exam-evaluation-system/
│
├── config.py                      ← Configuration (OCR engine selection)
├── app.py                         ← Flask application
├── requirements.txt               ← Dependencies (includes google-cloud-vision)
│
├── backend/
│   ├── ocr_processor.py          ← ⭐ Dual OCR engine implementation
│   ├── nlp_evaluator.py          ← Answer evaluation
│   ├── api.py                    ← API endpoints
│   └── ...
│
├── uploads/                       ← User uploaded images
├── database/                      ← SQLite database
│
└── Documentation:
    ├── GOOGLE_VISION_SETUP.md    ← Setup guide
    ├── INTEGRATION_SUMMARY.md    ← This integration summary
    ├── ARCHITECTURE.md           ← This file
    ├── README.md                 ← Updated with OCR info
    └── test_google_vision.py     ← Test script
```

## Environment Variables

```bash
# Primary Configuration
OCR_ENGINE=trocr                    # Options: trocr, google_vision, auto

# Google Cloud Vision (optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Other Settings
SECRET_KEY=your-secret-key
DEBUG=True
PORT=5000
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  • HTML5, CSS3, JavaScript                                  │
│  • Chart.js (visualizations)                                │
│  • Responsive design                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                           │
├─────────────────────────────────────────────────────────────┤
│  • Flask (Web framework)                                    │
│  • Python 3.8+                                              │
│  • SQLite (Database)                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      OCR Layer (NEW!)                        │
├─────────────────────────────────────────────────────────────┤
│  Option 1: TrOCR                                            │
│    • Hugging Face Transformers                              │
│    • PyTorch                                                │
│    • PIL/Pillow                                             │
│    • OpenCV                                                 │
│                                                              │
│  Option 2: Google Cloud Vision                              │
│    • google-cloud-vision library                            │
│    • REST API                                               │
│    • JSON credentials                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      NLP Layer                               │
├─────────────────────────────────────────────────────────────┤
│  • NLTK (Natural Language Toolkit)                          │
│  • scikit-learn (Machine Learning)                          │
│  • Semantic similarity                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Reporting Layer                           │
├─────────────────────────────────────────────────────────────┤
│  • ReportLab (PDF generation)                               │
└─────────────────────────────────────────────────────────────┘
```

## API Integration Example

```python
# Simple usage in your application code
from backend.ocr_processor import extract_text_from_image

# Automatic engine selection based on config
text = extract_text_from_image('student_answer.jpg')

# Force specific engine
trocr_text = extract_text_from_image('image.jpg', engine='trocr')
google_text = extract_text_from_image('image.jpg', engine='google_vision')

# Try Google, fallback to TrOCR if unavailable
auto_text = extract_text_from_image('image.jpg', engine='auto')
```

## Deployment Considerations

### Development Environment
```
✅ Use TrOCR
- No setup required
- No costs
- Good for testing
- Works offline
```

### Production Environment
```
✅ Use Google Cloud Vision
- Better accuracy
- Faster processing
- Professional quality
- Scalable
- Set up billing alerts
- Monitor usage
```

### Hybrid Approach
```
✅ Use Both
- Google Vision for critical exams
- TrOCR as fallback
- Cost optimization
- Maximum reliability
```

---

**Last Updated:** February 3, 2026  
**Version:** 2.0 - Dual OCR Engine Support
