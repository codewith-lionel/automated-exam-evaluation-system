# Quick Start Guide - Automated Exam Evaluation System

## 🎯 System is Ready!

All tests passed. The system is fully functional.

## 🚀 Start the Application

```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Run the application
python app.py
```

The application will start at: **http://localhost:5000**

## 🔐 Demo Credentials

**Student Account:**

- Email: `student@exam.com`
- Password: `Student@123`

**Admin Account:**

- Email: `admin@exam.com`
- Password: `Admin@123`

## 📝 How to Test Evaluation

### Option 1: Use Sample Files

1. Login as student
2. Go to Upload page
3. Upload: `sample_data/sample_student_answer.txt`
4. Fill in form:
   - Subject: Computer Science
   - Exam Type: Test
   - Total Marks: 60
5. In "Answer Key" field, paste the content from: `sample_data/model_answers_6questions.json`
6. Click "Upload & Evaluate"
7. View results with scores and feedback

### Option 2: Create Your Own Test

Create a text file with this format:

```
Q1: Your answer to question 1...
Q2: Your answer to question 2...
Q3: Your answer to question 3...
```

Then provide model answers in JSON format:

```json
{
  "questions": [
    {
      "question_number": 1,
      "question": "Question text",
      "model_answer": "Expected answer...",
      "max_marks": 10
    }
  ]
}
```

## ✅ What Works

- ✓ User authentication (signup/login/logout)
- ✓ File upload (images, PDFs, text files)
- ✓ OCR text extraction from images
- ✓ NLP-based answer evaluation
- ✓ Individual question scoring
- ✓ Keyword matching and analysis
- ✓ Automated feedback generation
- ✓ Interactive results with charts
- ✓ PDF report generation
- ✓ Admin dashboard with analytics

## 📊 Understanding Results

**Scoring Method:**

- System compares student answers with model answers
- Uses NLP (TF-IDF + Cosine Similarity)
- Extracts keywords from both answers
- Calculates similarity percentage
- Assigns marks based on similarity

**Score Ranges:**

- 90-100%: Excellent
- 80-89%: Very Good
- 70-79%: Good
- 60-69%: Satisfactory
- 50-59%: Pass
- Below 50%: Needs Work

**What Affects Scores:**

- Keyword coverage
- Concept depth
- Terminology match
- Answer completeness

## 🔧 Troubleshooting

**If application won't start:**

```bash
# Check if port 5000 is available
netstat -ano | findstr :5000

# Or change port in config.py
PORT = 5001
```

**If evaluation fails:**

- Make sure exam format has clear question numbers (Q1:, Q2:, etc.)
- Provide complete model answers
- Check that NLTK data is downloaded

**If OCR doesn't work:**

- Verify Tesseract path in config.py
- Use high-quality images (300+ DPI)
- Ensure text is clearly visible

## 📚 Important Files

- `app.py` - Main application
- `config.py` - Configuration (Tesseract path, etc.)
- `init_db.py` - Database initialization
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation
- `EVALUATION_GUIDE.md` - How evaluation works
- `TEST_RESULTS.md` - Test results summary

## 🎓 Example Workflow

1. **Student** scans completed exam paper
2. **Student** uploads to system via web interface
3. **System** extracts text using OCR
4. **Teacher** provides model answers
5. **System** evaluates each question individually
6. **System** generates scores and feedback
7. **Student** views results with detailed breakdown
8. **Student** downloads PDF report

## 🛠️ System Configuration

Current configuration:

- Database: SQLite (`database/exam_system.db`)
- Upload folder: `uploads/`
- Max file size: 10MB
- Allowed formats: PNG, JPG, JPEG, PDF
- Tesseract: Configured and working
- NLTK: Data downloaded and ready

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Check `EVALUATION_GUIDE.md` for evaluation details
3. Check `TEST_RESULTS.md` for test results
4. Run test scripts to diagnose issues:
   - `python test_system.py` - Full system check
   - `python test_database.py` - Database check
   - `python test_ocr.py` - OCR check
   - `python test_evaluation.py` - NLP check

---

**System Status: ✅ READY**

All components tested and working!
