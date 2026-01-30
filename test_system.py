"""Comprehensive system test"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*60)
    print("TESTING PYTHON MODULE IMPORTS")
    print("="*60)
    
    imports_to_test = [
        ('flask', 'Flask'),
        ('sqlite3', 'SQLite3'),
        ('nltk', 'NLTK'),
        ('sklearn', 'scikit-learn'),
        ('PIL', 'Pillow'),
        ('cv2', 'OpenCV'),
        ('pytesseract', 'Tesseract Python'),
        ('reportlab', 'ReportLab'),
        ('werkzeug.security', 'Werkzeug Security'),
    ]
    
    failed = []
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✓ {name:25} imported successfully")
        except ImportError as e:
            print(f"✗ {name:25} FAILED: {str(e)}")
            failed.append(name)
    
    if failed:
        print(f"\n✗ {len(failed)} module(s) failed to import")
        return False
    else:
        print("\n✓ All modules imported successfully")
        return True

def test_backend_modules():
    """Test backend module imports"""
    print("\n" + "="*60)
    print("TESTING BACKEND MODULES")
    print("="*60)
    
    backend_modules = [
        'backend.auth',
        'backend.api',
        'backend.database',
        'backend.nlp_evaluator',
        'backend.ocr_processor',
        'backend.pdf_generator',
        'backend.utils',
    ]
    
    failed = []
    for module in backend_modules:
        try:
            __import__(module)
            print(f"✓ {module:30} imported successfully")
        except Exception as e:
            print(f"✗ {module:30} FAILED: {str(e)}")
            failed.append(module)
    
    if failed:
        print(f"\n✗ {len(failed)} backend module(s) failed")
        return False
    else:
        print("\n✓ All backend modules imported successfully")
        return True

def test_directories():
    """Test required directories"""
    print("\n" + "="*60)
    print("TESTING DIRECTORY STRUCTURE")
    print("="*60)
    
    required_dirs = [
        'backend',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'database',
        'uploads',
        'sample_data',
    ]
    
    missing = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"✓ {dir_path:25} exists")
        else:
            print(f"✗ {dir_path:25} MISSING")
            missing.append(dir_path)
            # Create missing directories
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"  → Created {dir_path}")
            except Exception as e:
                print(f"  → Failed to create: {str(e)}")
    
    if missing:
        print(f"\n⚠ {len(missing)} directory(ies) were missing (created automatically)")
    else:
        print("\n✓ All required directories exist")
    
    return True

def test_config():
    """Test configuration"""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)
    
    from config import Config
    
    config_checks = [
        ('SECRET_KEY', Config.SECRET_KEY),
        ('DATABASE_PATH', Config.DATABASE_PATH),
        ('UPLOAD_FOLDER', Config.UPLOAD_FOLDER),
        ('TESSERACT_CMD', Config.TESSERACT_CMD),
    ]
    
    for name, value in config_checks:
        if value:
            print(f"✓ {name:20} = {value}")
        else:
            print(f"✗ {name:20} NOT SET")
    
    # Check Tesseract
    if os.path.exists(Config.TESSERACT_CMD):
        print(f"✓ Tesseract executable found")
    else:
        print(f"✗ Tesseract executable NOT FOUND at {Config.TESSERACT_CMD}")
        print(f"  → Update config.py with correct path")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("AUTOMATED EXAM EVALUATION SYSTEM - COMPREHENSIVE TEST")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Backend Modules", test_backend_modules),
        ("Directory Structure", test_directories),
        ("Configuration", test_config),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} TEST FAILED WITH ERROR:")
            print(f"   {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:30} {status}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ ALL TESTS PASSED - System is ready!")
    else:
        print("⚠ Some tests failed - Review errors above")
    
    print("="*60 + "\n")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
