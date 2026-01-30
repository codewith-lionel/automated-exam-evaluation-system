"""Test script to verify database structure and functionality"""
import sqlite3
import os

def test_database():
    db_path = 'database/exam_system.db'
    
    if not os.path.exists(db_path):
        print("✗ Database not found at", db_path)
        return False
    
    print("✓ Database file exists")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Tables found: {', '.join(tables)}")
        
        expected_tables = ['users', 'evaluations', 'questions', 'feedback', 'uploaded_files']
        for table in expected_tables:
            if table not in tables:
                print(f"✗ Missing table: {table}")
                return False
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Users in database: {user_count}")
        
        # Check evaluations
        cursor.execute("SELECT COUNT(*) FROM evaluations")
        eval_count = cursor.fetchone()[0]
        print(f"✓ Evaluations in database: {eval_count}")
        
        # Get sample user
        cursor.execute("SELECT email, role FROM users LIMIT 2")
        users = cursor.fetchall()
        if users:
            print("✓ Sample users:")
            for email, role in users:
                print(f"  - {email} ({role})")
        
        conn.close()
        print("\n✓ Database check PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        return False

if __name__ == '__main__':
    test_database()
