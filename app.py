"""Main Flask application."""

from flask import Flask, render_template, session, redirect, url_for
import os
from config import Config
from backend.auth import auth_bp
from backend.api import api_bp
from backend.nlp_evaluator import download_nltk_data

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Ensure required directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs('database', exist_ok=True)

# Download NLTK data on startup
print("Downloading required NLTK data...")
download_nltk_data()
print("NLTK data ready!")

# Template routes
@app.route('/')
def index():
    """Landing page - redirect based on authentication."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/home')
def home():
    """Public home page."""
    return render_template('home.html')

@app.route('/login')
def login():
    """Login/Signup page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page (requires authentication)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session)

@app.route('/upload')
def upload():
    """Upload page (requires authentication)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html', user=session)

@app.route('/results')
def results():
    """Results page (requires authentication)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('results.html', user=session)

@app.route('/results/<int:evaluation_id>')
def result_detail(evaluation_id):
    """Individual result detail page (requires authentication)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('result_detail.html', user=session, evaluation_id=evaluation_id)

@app.route('/feedback/<int:evaluation_id>')
def feedback(evaluation_id):
    """Feedback page (requires authentication)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('feedback.html', user=session, evaluation_id=evaluation_id)

@app.route('/profile')
def profile():
    """User profile page (requires authentication)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session)

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html', user=session if 'user_id' in session else None)

@app.route('/help')
def help_page():
    """Help page."""
    return render_template('help.html', user=session if 'user_id' in session else None)

@app.route('/admin')
def admin():
    """Admin panel (requires admin role)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('403.html'), 403
    return render_template('admin.html', user=session)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Check if database exists, if not, warn user
    if not os.path.exists(Config.DATABASE_PATH):
        print("\n" + "="*60)
        print("WARNING: Database not found!")
        print("Please run: python init_db.py")
        print("="*60 + "\n")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
