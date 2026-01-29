"""Utility functions for the application."""

import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder=None):
    """
    Save uploaded file with a unique name.
    
    Args:
        file: FileStorage object from request
        upload_folder: Optional custom upload folder
        
    Returns:
        Tuple of (filename, filepath, filesize)
    """
    if upload_folder is None:
        upload_folder = Config.UPLOAD_FOLDER
    
    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{unique_id}_{original_filename}"
    
    # Save file
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Get file size
    filesize = os.path.getsize(filepath)
    
    return filename, filepath, filesize

def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def parse_questions_from_text(text, model_answers=None):
    """
    Parse questions and answers from extracted text.
    
    This is a simple parser that looks for question patterns.
    Can be enhanced based on specific exam format.
    
    Args:
        text: Extracted text from OCR
        model_answers: Optional dict of model answers
        
    Returns:
        List of question dictionaries
    """
    import re
    
    questions = []
    
    # Split by question numbers (e.g., "1.", "Q1.", "Question 1:")
    question_pattern = r'(?:Question\s*\d+|Q\s*\d+|\d+\.)[\s:]*'
    parts = re.split(question_pattern, text, flags=re.IGNORECASE)
    
    # Remove empty first element if present
    if parts and not parts[0].strip():
        parts = parts[1:]
    
    for i, part in enumerate(parts):
        if part.strip():
            questions.append({
                'question_number': i + 1,
                'question_text': f'Question {i + 1}',
                'student_answer': part.strip(),
                'model_answer': model_answers.get(str(i + 1), '') if model_answers else '',
                'max_marks': 10  # Default marks per question
            })
    
    return questions

def calculate_grade(percentage):
    """
    Calculate letter grade based on percentage.
    
    Args:
        percentage: Score percentage (0-100)
        
    Returns:
        Letter grade (A+, A, B+, etc.)
    """
    if percentage >= 90:
        return 'A+'
    elif percentage >= 85:
        return 'A'
    elif percentage >= 80:
        return 'A-'
    elif percentage >= 75:
        return 'B+'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 65:
        return 'B-'
    elif percentage >= 60:
        return 'C+'
    elif percentage >= 55:
        return 'C'
    elif percentage >= 50:
        return 'C-'
    elif percentage >= 40:
        return 'D'
    else:
        return 'F'
