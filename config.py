import os

class Config:
    """Application configuration settings."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    DATABASE_PATH = 'database/exam_system.db'
    
    # File Upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Tesseract OCR path (adjust based on OS)
    # Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # Mac/Linux: '/usr/bin/tesseract' or '/usr/local/bin/tesseract'
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD') or '/usr/bin/tesseract'
    
    # Application settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
