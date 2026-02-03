"""
Quick test script for OCR on uploaded images.
Usage: python test_my_image.py <image_filename>
"""

import sys
import os
from backend.ocr_processor import extract_text_from_image

def test_image(image_path):
    """Test OCR on a specific image."""
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at: {image_path}")
        return
    
    print("=" * 70)
    print(f"Testing OCR on: {image_path}")
    print("=" * 70)
    print()
    
    # Extract text
    extracted_text = extract_text_from_image(image_path)
    
    print()
    print("=" * 70)
    print("EXTRACTED TEXT:")
    print("=" * 70)
    print(extracted_text)
    print("=" * 70)
    print(f"\nTotal characters: {len(extracted_text)}")
    print(f"Total words: {len(extracted_text.split())}")
    print()
    
    # Check for errors
    if "Error:" in extracted_text:
        print("⚠️  Extraction had issues. Check image quality.")
    else:
        print("✅ Extraction completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_my_image.py <image_filename>")
        print("\nExample:")
        print("  python test_my_image.py my_handwriting.jpg")
        print("  python test_my_image.py uploads/test.png")
        print("\nOr just provide the filename if it's in the current directory")
    else:
        image_path = sys.argv[1]
        test_image(image_path)
