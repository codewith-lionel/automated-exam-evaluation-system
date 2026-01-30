"""Database connection and query functions."""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from config import Config

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a database query with proper connection handling."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid

# User queries
def create_user(username, email, password_hash, role):
    """Create a new user."""
    query = '''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    '''
    return execute_query(query, (username, email, password_hash, role))

def get_user_by_email(email):
    """Get user by email."""
    query = 'SELECT * FROM users WHERE email = ?'
    return execute_query(query, (email,), fetch_one=True)

def get_user_by_id(user_id):
    """Get user by ID."""
    query = 'SELECT * FROM users WHERE id = ?'
    return execute_query(query, (user_id,), fetch_one=True)

def get_user_by_username(username):
    """Get user by username."""
    query = 'SELECT * FROM users WHERE username = ?'
    return execute_query(query, (username,), fetch_one=True)

# Evaluation queries
def create_evaluation(user_id, subject, exam_type, mode, total_marks, obtained_marks, percentage, status):
    """Create a new evaluation."""
    query = '''
        INSERT INTO evaluations (user_id, subject, exam_type, mode, total_marks, obtained_marks, percentage, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    return execute_query(query, (user_id, subject, exam_type, mode, total_marks, obtained_marks, percentage, status))

def get_evaluation(evaluation_id):
    """Get evaluation by ID."""
    query = 'SELECT * FROM evaluations WHERE id = ?'
    return execute_query(query, (evaluation_id,), fetch_one=True)

def get_user_evaluations(user_id, limit=None):
    """Get all evaluations for a user."""
    query = 'SELECT * FROM evaluations WHERE user_id = ? ORDER BY created_at DESC'
    if limit:
        query += f' LIMIT {limit}'
    return execute_query(query, (user_id,), fetch_all=True)

def get_all_evaluations(limit=None):
    """Get all evaluations (for admin)."""
    query = 'SELECT e.*, u.username, u.email FROM evaluations e JOIN users u ON e.user_id = u.id ORDER BY e.created_at DESC'
    if limit:
        query += f' LIMIT {limit}'
    return execute_query(query, fetch_all=True)

def update_evaluation_status(evaluation_id, status):
    """Update evaluation status."""
    query = 'UPDATE evaluations SET status = ? WHERE id = ?'
    execute_query(query, (status, evaluation_id))

# Question queries
def create_question(evaluation_id, question_number, question_text, model_answer, student_answer, max_marks, obtained_marks, keywords_matched, keywords_missed):
    """Create a new question."""
    query = '''
        INSERT INTO questions (evaluation_id, question_number, question_text, model_answer, student_answer, max_marks, obtained_marks, keywords_matched, keywords_missed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    return execute_query(query, (
        evaluation_id, question_number, question_text, model_answer, student_answer,
        max_marks, obtained_marks, json.dumps(keywords_matched), json.dumps(keywords_missed)
    ))

def get_evaluation_questions(evaluation_id):
    """Get all questions for an evaluation."""
    query = 'SELECT * FROM questions WHERE evaluation_id = ? ORDER BY question_number'
    return execute_query(query, (evaluation_id,), fetch_all=True)

# Feedback queries
def create_feedback(evaluation_id, good_answers, areas_to_improve, suggestions, additional_notes=''):
    """Create feedback for an evaluation."""
    query = '''
        INSERT INTO feedback (evaluation_id, good_answers, areas_to_improve, suggestions, additional_notes)
        VALUES (?, ?, ?, ?, ?)
    '''
    return execute_query(query, (
        evaluation_id,
        json.dumps(good_answers),
        json.dumps(areas_to_improve),
        json.dumps(suggestions),
        additional_notes
    ))

def get_evaluation_feedback(evaluation_id):
    """Get feedback for an evaluation."""
    query = 'SELECT * FROM feedback WHERE evaluation_id = ?'
    return execute_query(query, (evaluation_id,), fetch_one=True)

def update_feedback(evaluation_id, good_answers, areas_to_improve, suggestions, additional_notes=''):
    """Update feedback for an evaluation."""
    query = '''
        UPDATE feedback 
        SET good_answers = ?, areas_to_improve = ?, suggestions = ?, additional_notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE evaluation_id = ?
    '''
    execute_query(query, (
        json.dumps(good_answers),
        json.dumps(areas_to_improve),
        json.dumps(suggestions),
        additional_notes,
        evaluation_id
    ))

# File upload queries
def create_uploaded_file(evaluation_id, filename, file_path, file_size):
    """Record an uploaded file."""
    query = '''
        INSERT INTO uploaded_files (evaluation_id, filename, file_path, file_size)
        VALUES (?, ?, ?, ?)
    '''
    return execute_query(query, (evaluation_id, filename, file_path, file_size))

def get_evaluation_files(evaluation_id):
    """Get all files for an evaluation."""
    query = 'SELECT * FROM uploaded_files WHERE evaluation_id = ?'
    return execute_query(query, (evaluation_id,), fetch_all=True)

# Dashboard stats queries
def delete_evaluation(evaluation_id):
    """Delete an evaluation and all related data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Delete in order: feedback, questions, uploaded_files, then evaluation
        cursor.execute('DELETE FROM feedback WHERE evaluation_id = ?', (evaluation_id,))
        cursor.execute('DELETE FROM questions WHERE evaluation_id = ?', (evaluation_id,))
        cursor.execute('DELETE FROM uploaded_files WHERE evaluation_id = ?', (evaluation_id,))
        cursor.execute('DELETE FROM evaluations WHERE id = ?', (evaluation_id,))
        conn.commit()

def get_dashboard_stats(user_id=None, role='student'):
    """Get dashboard statistics."""
    stats = {}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if role == 'admin':
            # Total evaluations
            cursor.execute('SELECT COUNT(*) as count FROM evaluations')
            stats['total_evaluations'] = cursor.fetchone()['count']
            
            # Average score
            cursor.execute('SELECT AVG(percentage) as avg_score FROM evaluations WHERE status = "completed"')
            result = cursor.fetchone()
            stats['average_score'] = round(result['avg_score'], 2) if result['avg_score'] else 0
            
            # Total users
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "student"')
            stats['total_students'] = cursor.fetchone()['count']
        else:
            # Student stats
            cursor.execute('SELECT COUNT(*) as count FROM evaluations WHERE user_id = ?', (user_id,))
            stats['total_evaluations'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT AVG(percentage) as avg_score FROM evaluations WHERE user_id = ? AND status = "completed"', (user_id,))
            result = cursor.fetchone()
            stats['average_score'] = round(result['avg_score'], 2) if result['avg_score'] else 0
            
            cursor.execute('SELECT MAX(percentage) as max_score FROM evaluations WHERE user_id = ? AND status = "completed"', (user_id,))
            result = cursor.fetchone()
            stats['highest_score'] = round(result['max_score'], 2) if result['max_score'] else 0
    
    return stats
