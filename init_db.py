"""Database initialization script for the Automated Exam Evaluation System."""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the SQLite database with schema and sample data."""
    
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    db_path = 'database/exam_system.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create evaluations table
    cursor.execute('''
        CREATE TABLE evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject VARCHAR(100) NOT NULL,
            exam_type VARCHAR(50) NOT NULL,
            mode VARCHAR(20) NOT NULL,
            total_marks INTEGER NOT NULL,
            obtained_marks REAL NOT NULL,
            percentage REAL NOT NULL,
            status VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            model_answer TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            max_marks INTEGER NOT NULL,
            obtained_marks REAL NOT NULL,
            keywords_matched TEXT,
            keywords_missed TEXT,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id INTEGER NOT NULL,
            good_answers TEXT,
            areas_to_improve TEXT,
            suggestions TEXT,
            additional_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        )
    ''')
    
    # Create uploaded_files table
    cursor.execute('''
        CREATE TABLE uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX idx_evaluations_user_id ON evaluations(user_id)')
    cursor.execute('CREATE INDEX idx_questions_evaluation_id ON questions(evaluation_id)')
    cursor.execute('CREATE INDEX idx_feedback_evaluation_id ON feedback(evaluation_id)')
    
    # Insert demo users
    admin_password = generate_password_hash('Admin@123')
    student_password = generate_password_hash('Student@123')
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin@exam.com', admin_password, 'admin'))
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ('student', 'student@exam.com', student_password, 'student'))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {db_path}")
    print("\nDemo users created:")
    print("  Admin: admin@exam.com / Admin@123")
    print("  Student: student@exam.com / Student@123")

if __name__ == '__main__':
    init_database()
