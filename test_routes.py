"""Test Flask routes and templates"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from flask import url_for

def test_routes():
    """Test all Flask routes"""
    print("Testing Flask Routes and Templates\n" + "="*50)
    
    with app.test_client() as client:
        with app.app_context():
            routes_to_test = [
                ('/', 'Index/Landing'),
                ('/login', 'Login Page'),
                ('/dashboard', 'Dashboard'),
                ('/upload', 'Upload Page'),
                ('/results', 'Results List'),
                ('/profile', 'Profile Page'),
            ]
            
            print("\n✓ Testing public/redirect routes:")
            for route, name in routes_to_test:
                try:
                    response = client.get(route, follow_redirects=False)
                    status = response.status_code
                    if status in [200, 302]:  # 200 OK or 302 Redirect
                        print(f"  ✓ {route:20} -> {name:20} [Status: {status}]")
                    else:
                        print(f"  ✗ {route:20} -> {name:20} [Status: {status}] FAILED")
                except Exception as e:
                    print(f"  ✗ {route:20} -> {name:20} ERROR: {str(e)}")
            
            # Test API endpoints (should require auth or return 401/403)
            print("\n✓ Testing API endpoints:")
            api_routes = [
                '/api/auth/session',
                '/api/dashboard/stats',
                '/api/dashboard/recent',
            ]
            
            for route in api_routes:
                try:
                    response = client.get(route)
                    status = response.status_code
                    if status in [200, 401, 403]:  # OK or Unauthorized
                        print(f"  ✓ {route:35} [Status: {status}]")
                    else:
                        print(f"  ✗ {route:35} [Status: {status}] UNEXPECTED")
                except Exception as e:
                    print(f"  ✗ {route:35} ERROR: {str(e)}")
    
    # Check if templates exist
    print("\n✓ Checking template files:")
    template_dir = 'templates'
    required_templates = [
        'base.html', 'login.html', 'dashboard.html', 'upload.html',
        'results.html', 'result_detail.html', 'feedback.html',
        'profile.html', '404.html', '500.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            print(f"  ✓ {template:25} exists")
        else:
            print(f"  ✗ {template:25} MISSING")
    
    # Check static files
    print("\n✓ Checking static files:")
    static_checks = [
        ('static/css/variables.css', 'CSS Variables'),
        ('static/css/components.css', 'CSS Components'),
        ('static/css/layout.css', 'CSS Layout'),
        ('static/css/pages.css', 'CSS Pages'),
        ('static/js/main.js', 'Main JS'),
        ('static/js/auth.js', 'Auth JS'),
        ('static/js/dashboard.js', 'Dashboard JS'),
        ('static/js/upload.js', 'Upload JS'),
        ('static/js/results.js', 'Results JS'),
        ('static/js/utils.js', 'Utils JS'),
    ]
    
    for file_path, name in static_checks:
        if os.path.exists(file_path):
            print(f"  ✓ {name:20} exists")
        else:
            print(f"  ✗ {name:20} MISSING")
    
    print("\n" + "="*50)
    print("✓ Route and template check COMPLETE")

if __name__ == '__main__':
    test_routes()
