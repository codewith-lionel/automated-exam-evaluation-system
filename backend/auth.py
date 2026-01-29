"""Authentication routes and logic."""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import create_user, get_user_by_email, get_user_by_username
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    return True, "Valid"

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role'].lower()
        
        # Validate role
        if role not in ['admin', 'student']:
            return jsonify({'success': False, 'message': 'Invalid role. Must be admin or student'}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Check if user already exists
        if get_user_by_email(email):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        if get_user_by_username(username):
            return jsonify({'success': False, 'message': 'Username already taken'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = create_user(username, email, password_hash, role)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please login.',
            'user_id': user_id
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Get user
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user."""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout successful!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/api/auth/session', methods=['GET'])
def check_session():
    """Check current session."""
    try:
        if 'user_id' in session:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': session['user_id'],
                    'username': session['username'],
                    'email': session['email'],
                    'role': session['role']
                }
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'authenticated': False, 'message': str(e)}), 500

def login_required(f):
    """Decorator to require login for routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function
