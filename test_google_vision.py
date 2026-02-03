"""Test script to compare TrOCR vs Google Cloud Vision API."""

import os
import sys
from backend.ocr_processor import extract_text_from_image

def test_ocr_engines():
    """Test both OCR engines and compare results."""
    
    # Check for test image
    test_images = [
        'uploads/test_image.jpg',
        'sample_data/sample_student_answer.txt',  # If you have images
    ]
    
    # Find first available test image
    test_image = None
    for img in test_images:
        if os.path.exists(img) and img.endswith(('.jpg', '.png', '.jpeg')):
            test_image = img
            break
    
    if not test_image:
        print("❌ No test image found. Please place a test image in 'uploads/' folder")
        print("   Supported formats: .jpg, .png, .jpeg")
        return
    
    print("=" * 70)
    print("OCR ENGINE COMPARISON TEST")
    print("=" * 70)
    print(f"Test Image: {test_image}")
    print()
    
    # Test TrOCR
    print("🔹 Testing TrOCR (Local, Free)...")
    print("-" * 70)
    try:
        trocr_text = extract_text_from_image(test_image, engine='trocr')
        print(f"✅ TrOCR Result ({len(trocr_text)} chars):")
        print(trocr_text[:500])
        if len(trocr_text) > 500:
            print("... (truncated)")
    except Exception as e:
        print(f"❌ TrOCR Failed: {str(e)}")
        trocr_text = None
    
    print()
    print("=" * 70)
    print()
    
    # Test Google Vision
    print("🔹 Testing Google Cloud Vision API...")
    print("-" * 70)
    try:
        google_text = extract_text_from_image(test_image, engine='google_vision')
        print(f"✅ Google Vision Result ({len(google_text)} chars):")
        print(google_text[:500])
        if len(google_text) > 500:
            print("... (truncated)")
    except Exception as e:
        print(f"❌ Google Vision Failed: {str(e)}")
        if "not initialized" in str(e).lower():
            print()
            print("💡 To enable Google Vision:")
            print("   1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
            print("   2. See GOOGLE_VISION_SETUP.md for detailed instructions")
        google_text = None
    
    print()
    print("=" * 70)
    print()
    
    # Comparison
    if trocr_text and google_text:
        print("📊 COMPARISON:")
        print("-" * 70)
        print(f"TrOCR Length:         {len(trocr_text)} characters")
        print(f"Google Vision Length: {len(google_text)} characters")
        print()
        
        # Calculate similarity (simple metric)
        trocr_words = set(trocr_text.lower().split())
        google_words = set(google_text.lower().split())
        common_words = trocr_words & google_words
        
        if trocr_words:
            similarity = len(common_words) / len(trocr_words | google_words) * 100
            print(f"Word Overlap:         {similarity:.1f}%")
            print(f"Common Words:         {len(common_words)}")
    
    print()
    print("=" * 70)
    print("✅ Test Complete! Check GOOGLE_VISION_SETUP.md for setup instructions.")
    print("=" * 70)

if __name__ == '__main__':
    test_ocr_engines()
