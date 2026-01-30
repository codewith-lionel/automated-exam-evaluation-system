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
    
    This parser looks for question patterns and extracts individual answers.
    Supports multiple formats:
    - Q1: answer / Question 1: answer
    - 1. answer / 1) answer
    - Answer 1: answer / Ans 1: answer
    
    Args:
        text: Extracted text from OCR
        model_answers: Optional dict of model answers
        
    Returns:
        List of question dictionaries
    """
    import re
    
    questions = []
    
    if not text or not text.strip():
        return questions
    
    # Try to find question-answer pairs
    lines = text.split('\n')
    current_q_num = None
    current_answer = ''
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for question/answer number patterns
        patterns = [
            r'^(?:Q|Question|Ans|Answer)\s*(\d+)\s*[:.-]\s*(.*)$',  # Q1: or Answer 1:
            r'^(\d+)\s*[:.)]\s*(.*)$',  # 1. or 1) or 1:
        ]
        
        matched = False
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Save previous question if exists
                if current_q_num is not None and current_answer.strip():
                    questions.append({
                        'question_number': current_q_num,
                        'question_text': f'Question {current_q_num}',
                        'student_answer': current_answer.strip(),
                        'model_answer': model_answers.get(str(current_q_num), '') if model_answers else '',
                        'max_marks': 10
                    })
                
                # Start new question
                current_q_num = int(match.group(1))
                current_answer = match.group(2) if len(match.groups()) > 1 else ''
                matched = True
                break
        
        # If no pattern matched and we have a current question, append to it
        if not matched and current_q_num is not None:
            current_answer += ' ' + line
    
    # Save the last question
    if current_q_num is not None and current_answer.strip():
        questions.append({
            'question_number': current_q_num,
            'question_text': f'Question {current_q_num}',
            'student_answer': current_answer.strip(),
            'model_answer': model_answers.get(str(current_q_num), '') if model_answers else '',
            'max_marks': 10
        })
    
    # If no questions found, treat entire text as single answer
    if not questions and text.strip():
        questions.append({
            'question_number': 1,
            'question_text': 'Question 1',
            'student_answer': text.strip(),
            'model_answer': model_answers.get('1', '') if model_answers else '',
            'max_marks': 10
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
