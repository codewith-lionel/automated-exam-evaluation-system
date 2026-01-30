"""Test OCR processing"""
import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.ocr_processor import process_uploaded_file

def create_test_image():
    """Create a simple test image with text"""
    # Create a white image with black text
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use default font
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Add sample exam text
    text = """Q1: Object-Oriented Programming is a programming paradigm.
Q2: A class is a blueprint for creating objects.
Q3: An object is an instance of a class."""
    
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save test image
    test_path = 'uploads/test_ocr.png'
    os.makedirs('uploads', exist_ok=True)
    img.save(test_path)
    
    return test_path

def test_ocr():
    """Test OCR processing"""
    print("Testing OCR Processing\n" + "="*50)
    
    # Create test image
    print("\n✓ Creating test image...")
    test_image_path = create_test_image()
    print(f"  ✓ Test image created: {test_image_path}")
    
    # Test OCR
    print("\n✓ Running OCR on test image...")
    try:
        extracted_text = process_uploaded_file(test_image_path)
        
        if extracted_text and len(extracted_text.strip()) > 0:
            print("  ✓ OCR successful!")
            print("\n  Extracted text:")
            print("  " + "-"*46)
            for line in extracted_text.split('\n'):
                if line.strip():
                    print(f"  {line}")
            print("  " + "-"*46)
            print("\n✓ OCR test PASSED")
            return True
        else:
            print("  ✗ OCR returned empty text")
            return False
            
    except Exception as e:
        print(f"  ✗ OCR test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
if __name__ == '__main__':
    test_ocr()
