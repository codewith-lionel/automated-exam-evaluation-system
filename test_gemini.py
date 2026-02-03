"""Quick test script for Google Gemini OCR."""

import os
import sys

# Set API key for testing
os.environ['GEMINI_API_KEY'] = 'AIzaSyARcRLAGLT11QaC_2iX1u7ken0VMkmkT3g'
os.environ['OCR_ENGINE'] = 'gemini'

from backend.ocr_processor import extract_text_from_image

def test_gemini_ocr():
    """Test Gemini OCR with available images."""
    
    print("=" * 70)
    print("🚀 GOOGLE GEMINI OCR TEST")
    print("=" * 70)
    print()
    
    # Check if Gemini is configured
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not set!")
        print("   Run: setup_gemini.bat \"YOUR_API_KEY\"")
        return
    
    print(f"✅ API Key configured: {api_key[:20]}...")
    print(f"✅ OCR Engine: {os.getenv('OCR_ENGINE', 'auto')}")
    print()
    
    # Find test images
    test_folders = ['uploads', 'sample_data', '.']
    test_image = None
    
    for folder in test_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image = os.path.join(folder, file)
                    break
        if test_image:
            break
    
    if not test_image:
        print("❌ No test image found!")
        print("   Please place a test image in 'uploads/' folder")
        print("   Supported formats: .jpg, .jpeg, .png")
        print()
        
        # Create a simple test
        print("📝 Creating a quick text-based test instead...")
        print()
        test_gemini_api()
        return
    
    print(f"📄 Test Image: {test_image}")
    print("-" * 70)
    print()
    
    # Test Gemini OCR
    print("🔍 Extracting text with Gemini...")
    print()
    
    try:
        text = extract_text_from_image(test_image, engine='gemini')
        
        if text and not text.startswith("Error:"):
            print("✅ SUCCESS! Text extracted:")
            print("=" * 70)
            print(text)
            print("=" * 70)
            print()
            print(f"📊 Statistics:")
            print(f"   - Characters: {len(text)}")
            print(f"   - Words: {len(text.split())}")
            print(f"   - Lines: {len(text.splitlines())}")
        else:
            print(f"❌ FAILED: {text}")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)


def test_gemini_api():
    """Test Gemini API directly without image."""
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🧪 Testing Gemini API connection...")
        response = model.generate_content("Say 'Hello! Gemini is working!' in exactly those words.")
        
        print("✅ Gemini API Response:")
        print(response.text)
        print()
        print("✅ Gemini is properly configured and working!")
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Check your API key is valid")
        print("   2. Get a new key from: https://aistudio.google.com/app/apikey")
        print("   3. Run: pip install google-generativeai")


if __name__ == '__main__':
    print()
    test_gemini_ocr()
    print()
