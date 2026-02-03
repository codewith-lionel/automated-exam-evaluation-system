"""
Test script for TrOCR implementation.
Creates a sample handwritten-style image and tests the OCR functionality.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Import OCR processor
from backend.ocr_processor import extract_text_from_image

def create_sample_image():
    """Create a simple test image with text."""
    # Create white background
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text (simulating handwritten content)
    test_text = """Question 1: What is Python?
    
    Answer: Python is a high-level programming language
    that is widely used for web development, data science,
    and automation tasks. It is known for its simple syntax
    and readability."""
    
    # Use default font
    draw.text((50, 50), test_text, fill='black')
    
    # Save image
    test_image_path = 'test_sample.png'
    img.save(test_image_path)
    print(f"Created test image: {test_image_path}")
    
    return test_image_path

def test_ocr():
    """Test OCR functionality with TrOCR."""
    print("=" * 60)
    print("Testing TrOCR Implementation")
    print("=" * 60)
    
    # Create sample image
    image_path = create_sample_image()
    
    print("\nProcessing image with TrOCR...")
    print("-" * 60)
    
    # Extract text
    extracted_text = extract_text_from_image(image_path)
    
    print("\n" + "=" * 60)
    print("EXTRACTED TEXT:")
    print("=" * 60)
    print(extracted_text)
    print("=" * 60)
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"\nCleaned up test image: {image_path}")
    
    # Check if extraction was successful
    if "Error:" not in extracted_text and len(extracted_text) > 20:
        print("\n✓ SUCCESS: TrOCR is working correctly!")
        return True
    else:
        print("\n✗ FAILED: TrOCR extraction unsuccessful")
        return False

if __name__ == "__main__":
    test_ocr()
