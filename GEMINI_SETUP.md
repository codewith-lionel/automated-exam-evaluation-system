# 🎉 Google Gemini API - Quick Setup Guide

## What is Google Gemini?

**Google Gemini** is Google's most advanced AI model that can:
- ✅ Read text from images (OCR)
- ✅ Understand context and meaning
- ✅ Generate intelligent feedback
- ✅ Work with handwritten and printed text
- ✅ Process images directly

## Why Use Gemini Over Other OCR?

| Feature | TrOCR | Google Vision | **Gemini** |
|---------|-------|---------------|------------|
| Setup | None | Complex (JSON) | **Simple (API key)** |
| Cost | Free | $1.50/1000* | **Free tier available** |
| Accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| Intelligence | Basic | Good | **AI-Powered** |
| Speed | Moderate | Fast | **Very Fast** |
| Setup Time | 0 min | 30 min | **2 minutes** |

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your API Key (30 seconds)

1. Visit: **https://aistudio.google.com/app/apikey**
2. Click **"Get API Key"** → **"Create API Key"**
3. Copy your API key (starts with `AIza...`)

### Step 2: Configure Your System (30 seconds)

**Method A: Use the Setup Script (Easiest)**
```bash
setup_gemini.bat "YOUR_API_KEY_HERE"
```

**Method B: Set Environment Variables Manually**

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="AIzaSyAbc123YourKeyHere"
$env:OCR_ENGINE="gemini"
```

Windows CMD:
```cmd
set GEMINI_API_KEY=AIzaSyAbc123YourKeyHere
set OCR_ENGINE=gemini
```

### Step 3: Run Your App (10 seconds)
```bash
python app.py
```

That's it! 🎉

## 📝 Usage Examples

### In Your Application
```python
from backend.ocr_processor import extract_text_from_image

# Automatic (uses Gemini if configured)
text = extract_text_from_image('exam_paper.jpg')

# Force Gemini
text = extract_text_from_image('exam_paper.jpg', engine='gemini')
```

### Test It
```bash
python test_google_vision.py
```

## 💰 Pricing

### Gemini API Free Tier:
- **FREE**: 60 requests per minute
- **FREE**: Generous daily quota
- **No credit card required** for free tier

### Gemini API Paid (if you need more):
- Extremely affordable
- Pay only for what you use
- Much cheaper than other AI services

## ⚙️ Configuration Options

### Environment Variables:
```bash
GEMINI_API_KEY       Your Gemini API key
OCR_ENGINE           Set to "gemini" to use Gemini
```

### In config.py:
```python
GEMINI_API_KEY = "AIzaSyAbc123YourKeyHere"
OCR_ENGINE = 'gemini'
```

## 🎯 Gemini vs Others - When to Use What?

### Use **Gemini** when:
- ✅ You want the BEST accuracy
- ✅ You need AI-powered text understanding
- ✅ You want simple setup (just API key)
- ✅ You're processing complex documents
- ✅ You need handwritten text recognition
- ✅ You want future AI evaluation features

### Use **TrOCR** when:
- ✅ You need 100% offline/local processing
- ✅ You have privacy requirements
- ✅ You want zero cost forever
- ✅ Internet not available

### Use **Google Cloud Vision** when:
- ✅ You already have Vision API setup
- ✅ You need enterprise features
- ✅ You want traditional OCR API

## 🔒 Security Best Practices

### ⚠️ IMPORTANT:
1. **Never commit API keys to Git**
2. **Use environment variables**
3. **Add `.env` to `.gitignore`**
4. **Regenerate if exposed**

### Secure Setup:
```bash
# Create .env file (add to .gitignore!)
echo GEMINI_API_KEY=AIzaSyAbc123YourKeyHere > .env
echo OCR_ENGINE=gemini >> .env
```

## 🧪 Testing

### Test Gemini OCR:
```python
# Run the test script
python test_google_vision.py
```

### Quick Test in Python:
```python
import google.generativeai as genai
from PIL import Image

# Configure
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

# Test
img = Image.open('test_image.jpg')
response = model.generate_content(["Extract text from this image", img])
print(response.text)
```

## 🆘 Troubleshooting

### Error: "API key not valid"
**Solution:**
- ✅ Check you copied the full API key
- ✅ Regenerate key if needed
- ✅ Verify environment variable is set: `echo $env:GEMINI_API_KEY`

### Error: "Gemini not initialized"
**Solution:**
- ✅ Set `GEMINI_API_KEY` environment variable
- ✅ Restart your terminal/IDE
- ✅ Verify: `python -c "import os; print(os.getenv('GEMINI_API_KEY'))"`

### Error: "Module not found: google.generativeai"
**Solution:**
```bash
pip install google-generativeai
```

### Gemini not being used?
**Solution:**
- ✅ Set `OCR_ENGINE=gemini` environment variable
- ✅ Check console output for "Using OCR engine: gemini"
- ✅ Restart application after setting variables

## 🎁 Bonus: AI-Powered Evaluation

Gemini can do MORE than just OCR! You can use it for:

### Intelligent Answer Evaluation:
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = f"""
Evaluate this student answer against the model answer:

Model Answer: {model_answer}
Student Answer: {student_answer}

Provide:
1. Score out of 10
2. Strengths
3. Areas for improvement
4. Suggestions
"""

response = model.generate_content(prompt)
print(response.text)
```

## 📚 Additional Resources

- 🌐 [Gemini API Documentation](https://ai.google.dev/docs)
- 🔑 [Get API Key](https://aistudio.google.com/app/apikey)
- 💰 [Pricing Details](https://ai.google.dev/pricing)
- 📖 [Python SDK Guide](https://ai.google.dev/tutorials/python_quickstart)

## ✨ What's Next?

Now that Gemini is set up, you can:

1. ✅ **Test OCR**: Upload an exam and see results
2. 🚀 **Compare Engines**: Run `python test_google_vision.py`
3. 🎯 **Enhance Evaluation**: Use Gemini for AI-powered feedback
4. 📊 **Monitor Usage**: Check your API usage in Google AI Studio

## 🎉 Summary

```
✅ Simple setup (just API key)
✅ Superior accuracy
✅ AI-powered intelligence
✅ Free tier available
✅ Fast processing
✅ Easy to use
```

**You're all set to use Google Gemini! 🚀**

---

**Need help?** Check the troubleshooting section or run `python test_google_vision.py` to diagnose issues.

**Last Updated:** February 3, 2026
