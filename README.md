# ExamEval AI - Automated Examination Evaluation System

![ExamEval AI Logo](static/images/logo.svg)

**Smarter Assessments. Fairer Futures.**

A comprehensive web-based automated examination evaluation system that uses OCR (Optical Character Recognition) and NLP (Natural Language Processing) to evaluate both handwritten scanned and typed exam answers. Built with Flask, Tesseract OCR, NLTK, and modern web technologies.

## ✨ Features

### Core Functionality

- 🔐 **Secure Authentication** - Role-based access control (Admin/Teacher and Student)
- 📤 **Smart Upload System** - Drag-and-drop file upload with support for PNG, JPG, JPEG, PDF
- 🔍 **OCR Processing** - Extract text from scanned exam papers using Tesseract OCR
- 🤖 **NLP Evaluation** - Intelligent answer evaluation using NLTK and scikit-learn
- 📊 **Visual Results** - Interactive charts and detailed breakdowns with Chart.js
- 💬 **Feedback System** - Categorized feedback with strengths, improvements, and suggestions
- 📄 **PDF Reports** - Professional evaluation reports with ReportLab
- 📈 **Analytics Dashboard** - Role-based dashboards with KPIs and performance metrics

### User Interface

- 🌙 **Dark Theme** - Professional dark theme with optional light mode toggle
- 📱 **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- ♿ **Accessible** - WCAG 2.1 AA compliant with keyboard navigation
- 🎨 **Professional UI/UX** - Modern design with smooth animations and micro-interactions
- 🔔 **Real-time Notifications** - Toast notifications for user feedback

## 🚀 Quick Start

### Prerequisites

Before installation, ensure you have the following installed:

1. **Python 3.8 or higher**

   ```bash
   python --version
   ```

2. **Git**

   ```bash
   git --version
   ```

3. **Tesseract OCR** (Required for OCR functionality)

   **Windows:**
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR\`
   - Add to PATH or update `config.py` with installation path

   **macOS:**

   ```bash
   brew install tesseract
   ```

   **Linux (Ubuntu/Debian):**

   ```bash
   sudo apt update
   sudo apt install tesseract-ocr
   sudo apt install libtesseract-dev
   ```

   **Verify installation:**

   ```bash
   tesseract --version
   ```

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/codewith-lionel/automated-exam-evaluation-system.git
   cd automated-exam-evaluation-system
   ```

2. **Create and activate virtual environment**

   **Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Tesseract path (if needed)**

   Edit `config.py` and update the `TESSERACT_CMD` path:

   ```python
   # Windows
   TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

   # macOS/Linux (usually auto-detected)
   TESSERACT_CMD = '/usr/bin/tesseract'  # or '/usr/local/bin/tesseract'
   ```

5. **Download NLTK data**

   The application will automatically download required NLTK data on first run, but you can also do it manually:

   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
   ```

6. **Initialize the database**

   ```bash
   python init_db.py
   ```

   This will create:
   - SQLite database at `database/exam_system.db`
   - Demo admin user: `admin@exam.com` / `Admin@123`
   - Demo student user: `student@exam.com` / `Student@123`

7. **Run the application**

   ```bash
   python app.py
   ```

8. **Access the application**

   Open your browser and navigate to:

   ```
   http://localhost:5000
   ```

## 📖 Usage Guide

### For Students

1. **Login** with your credentials or sign up for a new account
2. **Navigate to Upload** page from the dashboard
3. **Upload your exam**:
   - Select file (PNG, JPG, JPEG, or PDF)
   - Fill in exam details (Subject, Type, Total Marks)
   - Choose mode: Offline (Scanned) or Online (Typed)
4. **Review extracted text** (for scanned papers) and make corrections if needed
5. **Submit for evaluation** after providing model answers for each question
6. **View results** with detailed breakdown, charts, and feedback
7. **Download PDF report** for your records

### For Teachers/Admins

1. **Login** with admin credentials
2. **Access Admin Dashboard** to view:
   - Total evaluations
   - Average scores
   - Recent student activities
3. **Review student submissions** from the Results page
4. **Edit feedback** for any evaluation
5. **Generate PDF reports** for distribution

## 📝 Exam Paper Format Guidelines

### Important: Structuring Student Answers

For accurate evaluation, student exam papers must follow a structured format. The system needs to identify individual question answers.

#### ✅ Supported Formats

**Format 1: Numbered with Period**

```
1. Object-Oriented Programming is a programming paradigm based on objects...
2. A class is a blueprint for creating objects while an object is an instance...
3. Encapsulation is the bundling of data and methods within a class...
```

**Format 2: Question Prefix**

```
Q1: Object-Oriented Programming is a programming paradigm based on objects...
Q2: A class is a blueprint for creating objects while an object is an instance...
Q3: Encapsulation is the bundling of data and methods within a class...
```

**Format 3: Answer Prefix**

```
Answer 1: Object-Oriented Programming is a programming paradigm based on objects...
Answer 2: A class is a blueprint for creating objects while an object is an instance...
Answer 3: Encapsulation is the bundling of data and methods within a class...
```

#### ❌ What Doesn't Work

- **No numbering or markers** - System cannot identify where one answer ends and another begins
- **Inconsistent formatting** - Mixing different styles within the same paper
- **Poor OCR quality** - Illegible handwriting or low-quality scans

### Model Answer Format

When providing model answers (answer key), use one of these formats:

**Format 1: JSON (Recommended)**

```json
{
  "questions": [
    {
      "question_number": 1,
      "question": "What is OOP?",
      "model_answer": "Object-Oriented Programming is a paradigm...",
      "max_marks": 10
    },
    {
      "question_number": 2,
      "question": "Explain class vs object.",
      "model_answer": "A class is a blueprint...",
      "max_marks": 10
    }
  ]
}
```

**Format 2: Structured Text**

```
Q1: What is OOP?
A1: Object-Oriented Programming is a paradigm based on objects...

Q2: Explain class vs object.
A2: A class is a blueprint for creating objects...
```

### Tips for Best Results

1. **Clear Handwriting** - For scanned papers, ensure handwriting is legible
2. **Good Scan Quality** - Use 300 DPI or higher, avoid shadows and creases
3. **Consistent Numbering** - Start from 1 and increment sequentially
4. **One Question Per Section** - Don't mix multiple sub-questions without clear markers
5. **Provide Complete Model Answers** - The more detailed your model answer, the better the evaluation

### Example Workflow

1. **Student writes exam** following format (e.g., "Q1: answer", "Q2: answer")
2. **Scan or photograph** the exam paper
3. **Upload** to the system
4. **System extracts text** using OCR
5. **Provide model answers** in JSON or structured text format
6. **System parses** student answers by question number
7. **NLP evaluation** compares each student answer with corresponding model answer
8. **View results** with per-question breakdown

## 🏗️ Project Structure

```
automated-exam-evaluation-system/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── init_db.py                      # Database initialization
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── backend/                        # Backend modules
│   ├── __init__.py
│   ├── auth.py                     # Authentication logic
│   ├── api.py                      # API routes
│   ├── database.py                 # Database queries
│   ├── ocr_processor.py            # OCR with Tesseract
│   ├── nlp_evaluator.py            # NLP evaluation with NLTK
│   ├── pdf_generator.py            # PDF reports with ReportLab
│   └── utils.py                    # Helper functions
│
├── static/                         # Static assets
│   ├── css/
│   │   ├── variables.css           # CSS custom properties
│   │   ├── components.css          # Reusable components
│   │   ├── layout.css              # Layout styles
│   │   └── pages.css               # Page-specific styles
│   ├── js/
│   │   ├── main.js                 # Core JavaScript
│   │   ├── auth.js                 # Authentication
│   │   ├── dashboard.js            # Dashboard functionality
│   │   ├── upload.js               # Upload functionality
│   │   ├── results.js              # Results display
│   │   └── utils.js                # Helper functions
│   └── images/
│       └── logo.svg                # Application logo
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── login.html                  # Login/Signup page
│   ├── dashboard.html              # Dashboard
│   ├── upload.html                 # Upload page
│   ├── results.html                # Results listing
│   ├── result_detail.html          # Detailed result view
│   ├── feedback.html               # Feedback page
│   ├── profile.html                # User profile
│   ├── 404.html                    # Not found page
│   └── 500.html                    # Server error page
│
├── database/                       # Database files (gitignored)
│   └── exam_system.db
│
├── uploads/                        # Uploaded files (gitignored)
│
└── sample_data/                    # Sample test data
    ├── model_answers.json          # Sample model answers
    └── README.md                   # Sample data documentation
```

## 🔧 API Documentation

### Authentication Endpoints

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/session` - Check current session

### Dashboard Endpoints

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent` - Get recent activities

### Evaluation Endpoints

- `POST /api/upload` - Upload exam file and extract text
- `POST /api/evaluate` - Evaluate answers with NLP
- `GET /api/results/<id>` - Get evaluation result by ID
- `GET /api/results` - Get all results (paginated)
- `PUT /api/feedback/<id>` - Update feedback (Admin only)
- `GET /api/results/<id>/pdf` - Download PDF report

### User Endpoints

- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

## 🧪 Testing

### Sample Credentials

**Admin/Teacher Account:**

- Email: `admin@exam.com`
- Password: `Admin@123`

**Student Account:**

- Email: `student@exam.com`
- Password: `Student@123`

### Test Workflow

1. Login with student credentials
2. Upload a sample exam (you can create a simple text file or image)
3. Provide model answers from `sample_data/model_answers.json`
4. View evaluation results with charts and feedback
5. Download PDF report

## 🛠️ Technology Stack

### Backend

- **Flask 3.0.0** - Web framework
- **SQLite** - Database
- **Tesseract OCR** - Text extraction from images
- **NLTK 3.8.1** - Natural language processing
- **scikit-learn 1.3.2** - Machine learning (TF-IDF, cosine similarity)
- **ReportLab 4.0.7** - PDF generation
- **Pillow 10.1.0** - Image processing
- **OpenCV** - Image preprocessing

### Frontend

- **HTML5** - Semantic markup
- **CSS3** - Styling with custom properties
- **Vanilla JavaScript (ES6+)** - Client-side logic
- **Chart.js 4.4.0** - Data visualizations
- **Font Awesome 6.4.0** - Icons

## 🔒 Security Features

- ✅ Password hashing with `werkzeug.security` (pbkdf2:sha256)
- ✅ SQL injection prevention (parameterized queries)
- ✅ File upload validation (type and size limits)
- ✅ Secure session management with httponly cookies
- ✅ Input sanitization for text fields
- ✅ Role-based access control
- ✅ CSRF protection for forms

## ♿ Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader compatible
- Proper ARIA labels
- Sufficient color contrast (4.5:1 for normal text)
- Semantic HTML structure

## 🐛 Troubleshooting

### Tesseract Not Found

**Error:** `pytesseract.pytesseract.TesseractNotFoundError`

**Solution:**

1. Verify Tesseract is installed: `tesseract --version`
2. Update `config.py` with correct Tesseract path
3. Ensure Tesseract is in your system PATH

### NLTK Data Missing

**Error:** `LookupError: Resource punkt not found`

**Solution:**

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
```

### Database Not Found

**Error:** `sqlite3.OperationalError: unable to open database file`

**Solution:**

```bash
python init_db.py
```

### Port Already in Use

**Error:** `OSError: [Errno 98] Address already in use`

**Solution:**

```bash
# Kill process on port 5000
# Linux/Mac:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in config.py
PORT = 5001
```

### Image Upload Fails

**Error:** File upload returns 400 error

**Solution:**

1. Check file size (max 10MB)
2. Verify file format (PNG, JPG, JPEG, PDF only)
3. Ensure `uploads/` directory exists and is writable

## 📊 Performance Optimization

- Image compression before OCR processing
- Database indexing on frequently queried columns
- Efficient NLP algorithms (TF-IDF + cosine similarity)
- Static asset caching
- Lazy loading for heavy components

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Authors

- **Lionel** - [codewith-lionel](https://github.com/codewith-lionel)

## 🙏 Acknowledgments

- Tesseract OCR by Google
- NLTK team for natural language processing tools
- Flask framework developers
- Chart.js for beautiful visualizations
- Font Awesome for icons

## 📧 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Email: support@exameval.ai (example)

## 🗺️ Roadmap

- [ ] Multi-language support for OCR
- [ ] Advanced plagiarism detection
- [ ] Real-time collaboration for teachers
- [ ] Mobile app (iOS/Android)
- [ ] Integration with LMS platforms (Moodle, Canvas)
- [ ] Video answer evaluation
- [ ] AI-powered question generation

---

**Made with ❤️ by the ExamEval AI Team**

_Smarter Assessments. Fairer Futures._
