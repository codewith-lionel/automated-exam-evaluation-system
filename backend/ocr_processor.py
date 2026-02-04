"""OCR processor supporting TrOCR and Google Cloud Vision API for text extraction from images."""

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
import os
import re
import torch
from io import BytesIO

# Initialize Google Gemini API client
gemini_model = None
try:
    import google.generativeai as genai
    from config import Config
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Use gemini-2.5-flash (latest fast model with vision support)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        print("Google Gemini API client initialized successfully")
except Exception as e:
    print(f"INFO: Google Gemini not available: {str(e)}")

# Google Cloud Vision and TrOCR disabled - using Gemini only
vision_client = None
processor = None
model = None
print("Using Google Gemini for OCR (TrOCR and Google Vision disabled)")


def process_image_with_trocr(pil_image):
    """
    Process a PIL image with TrOCR model.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        Extracted text as string
    """
    try:
        # Prepare image for model
        pixel_values = processor(pil_image, return_tensors="pt").pixel_values
        
        # Move to same device as model
        device = next(model.parameters()).device
        pixel_values = pixel_values.to(device)
        
        # Generate text with better parameters
        with torch.no_grad():
            generated_ids = model.generate(
                pixel_values,
                max_length=512,
                num_beams=4,
                early_stopping=True
            )
        
        # Decode text
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return generated_text
    
    except Exception as e:
        print(f"Error in TrOCR processing: {str(e)}")
        return ""


def split_image_into_patches(image, patch_size=1024, overlap=100):
    """
    Split a large image into overlapping patches for processing.
    
    Args:
        image: PIL Image object
        patch_size: Size of each patch
        overlap: Overlap between patches
        
    Returns:
        List of PIL Image patches
    """
    patches = []
    width, height = image.size
    
    stride = patch_size - overlap
    
    for y in range(0, height, stride):
        for x in range(0, width, stride):
            # Calculate patch boundaries
            left = x
            top = y
            right = min(x + patch_size, width)
            bottom = min(y + patch_size, height)
            
            # Skip if patch is too small
            if right - left < 200 or bottom - top < 200:
                continue
            
            # Crop patch
            patch = image.crop((left, top, right, bottom))
            patches.append(patch)
    
    return patches


def extract_text_line_regions(pil_image):
    """
    Extract individual text line regions from an image for line-by-line processing.
    TrOCR works better when processing individual text lines.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        List of PIL Image objects, one per text line
    """
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(pil_image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Use horizontal projection to find text lines
        height, width = thresh.shape
        horizontal_projection = np.sum(thresh, axis=1)
        
        # Find line boundaries
        line_regions = []
        in_line = False
        line_start = 0
        threshold = width * 0.05  # Adjust sensitivity
        
        for i, value in enumerate(horizontal_projection):
            if value > threshold and not in_line:
                # Start of a line
                line_start = i
                in_line = True
            elif value <= threshold and in_line:
                # End of a line
                line_end = i
                in_line = False
                
                # Add padding
                padding = 5
                y1 = max(0, line_start - padding)
                y2 = min(height, line_end + padding)
                
                # Extract line region
                if y2 - y1 > 20:  # Minimum line height
                    line_img = pil_image.crop((0, y1, width, y2))
                    line_regions.append(line_img)
        
        # Handle case where line extends to bottom
        if in_line:
            y1 = max(0, line_start - 5)
            line_img = pil_image.crop((0, y1, width, height))
            line_regions.append(line_img)
        
        print(f"Found {len(line_regions)} text line(s)")
        return line_regions
    
    except Exception as e:
        print(f"Error extracting text lines: {str(e)}")
        return []


def clean_ocr_text(text):
    """
    Clean OCR-extracted text to improve quality.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Cleaned text
    """
    if not text or text.startswith("Error:"):
        return text
    
    # Remove excessive special characters and artifacts
    # Replace common OCR mistakes
    replacements = {
        '|': 'I',  # Vertical bars often misread as I
        '~': '-',  # Tildes to dashes
        '_': ' ',  # Underscores to spaces
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove standalone special characters
    text = re.sub(r'\s+[^\w\s]\s+', ' ', text)
    
    # Remove lines with too many special characters (likely noise)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Count alphanumeric vs special chars
        alphanum = sum(c.isalnum() for c in line)
        special = sum(not c.isalnum() and not c.isspace() for c in line)
        
        # Keep line if it has more alphanumeric than special characters
        if alphanum > special or len(line.strip()) > 50:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Normalize whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single
    
    return text.strip()


def preprocess_image_for_trocr(image_path):
    """
    Preprocess image for TrOCR model.
    TrOCR requires less aggressive preprocessing than traditional OCR.
    
    Steps:
    1. Load image
    2. Basic denoising
    3. Light contrast enhancement
    4. Convert to RGB (TrOCR expects RGB)
    """
    try:
        # Read image with OpenCV
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError("Failed to load image")
        
        # Convert BGR to RGB (TrOCR expects RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Light denoising only (TrOCR handles noise well)
        img_rgb = cv2.fastNlMeansDenoisingColored(img_rgb, None, 5, 5, 7, 21)
        
        # Light contrast enhancement
        pil_image = Image.fromarray(img_rgb)
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        print(f"Preprocessed image: {image_path}")
        return pil_image
    
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        # Return original image as PIL
        return Image.open(image_path).convert('RGB')

def extract_text_gemini(image_path):
    """
    Extract text from image using Google Gemini AI.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        if gemini_model is None:
            raise Exception("Google Gemini API not initialized. Please set GEMINI_API_KEY in .env file.")
        
        print(f"Processing image with Google Gemini: {image_path}")
        
        # Verify file exists
        if not os.path.exists(image_path):
            raise Exception(f"Image file not found: {image_path}")
        
        # Read and prepare image
        from PIL import Image as PILImage
        img = PILImage.open(image_path)
        print(f"Image loaded: {img.size} pixels, mode: {img.mode}")
        
        # Create prompt for OCR
        prompt = """Extract all text from this image. 
        
Rules:
- Extract ALL visible text exactly as it appears
- Maintain line breaks and formatting
- Include handwritten and printed text
- Do not add any explanations or comments
- Only output the extracted text"""
        
        print("Sending request to Gemini API...")
        # Generate content
        response = gemini_model.generate_content([prompt, img])
        print("Response received from Gemini API")
        
        if response.text:
            extracted_text = response.text.strip()
            print(f"Gemini extracted {len(extracted_text)} characters")
            print(f"Preview: {extracted_text[:200]}...")
            cleaned_text = clean_ocr_text(extracted_text)
            print(f"After cleaning: {len(cleaned_text)} characters")
            return cleaned_text
        else:
            print("WARNING: No text detected by Gemini")
            return "Error: No text detected in the image. Please ensure the image contains readable text."
    
    except Exception as e:
        error_msg = f"Gemini OCR failed: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return f"Error: {error_msg}"


def extract_text_google_vision(image_path):
    """
    Extract text from image using Google Cloud Vision API.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        if vision_client is None:
            raise Exception("Google Cloud Vision API not initialized. Please set GOOGLE_APPLICATION_CREDENTIALS.")
        
        print(f"Processing image with Google Cloud Vision: {image_path}")
        
        # Read the image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Create Image object
        image = vision.Image(content=content)
        
        # Perform text detection
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        if response.error.message:
            raise Exception(f'Google Vision API error: {response.error.message}')
        
        # Extract full text
        if texts:
            extracted_text = texts[0].description
            print(f"Google Vision extracted {len(extracted_text)} characters")
            print(f"Preview: {extracted_text[:200]}...")
            return clean_ocr_text(extracted_text)
        else:
            print("WARNING: No text detected by Google Vision")
            return "Error: No text detected in the image"
    
    except Exception as e:
        error_msg = f"Google Vision OCR failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}"


def extract_text_from_image(image_path, engine='auto'):
    """
    Extract text from image using specified OCR engine.
    Supports TrOCR (local), Google Cloud Vision (cloud), and Google Gemini (AI).
    
    Args:
        image_path: Path to the image file
        engine: OCR engine to use ('trocr', 'google_vision', 'gemini', or 'auto')
               'auto' will use configured engine from environment
        
    Returns:
        Extracted text as string
    """
    try:
        # Determine which engine to use
        from config import Config
        
        if engine == 'auto':
            engine = Config.OCR_ENGINE
        
        print(f"Using OCR engine: {engine}")
        
        # Route to appropriate OCR engine (Gemini only)
        if engine == 'gemini' or engine == 'auto':
            return extract_text_gemini(image_path)
        elif engine == 'google_vision':
            return "Error: Google Vision is disabled. Using Gemini only."
        elif engine == 'trocr':
            return "Error: TrOCR is disabled. Using Gemini only."
        else:
            # Always use Gemini
            return extract_text_gemini(image_path)
    
    except Exception as e:
        error_msg = f"OCR extraction failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}"


def extract_text_trocr(image_path):
    """
    Extract text from image using TrOCR model.
    Optimized for handwritten text.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        # Verify TrOCR model is loaded
        if processor is None or model is None:
            raise Exception("TrOCR model not loaded. Please check installation.")
        
        # Preprocess image
        print(f"Processing image with TrOCR: {image_path}")
        pil_image = preprocess_image_for_trocr(image_path)
        
        # Try to detect text lines first
        text_lines = extract_text_line_regions(pil_image)
        
        extracted_texts = []
        
        if text_lines and len(text_lines) > 1:
            # Process line by line
            print(f"Processing {len(text_lines)} detected text lines")
            
            for i, line_img in enumerate(text_lines):
                try:
                    text = process_image_with_trocr(line_img)
                    if text.strip():
                        extracted_texts.append(text)
                        print(f"Line {i+1}/{len(text_lines)}: '{text[:50]}...'")
                except Exception as e:
                    print(f"Error processing line {i+1}: {str(e)}")
        else:
            # Fall back to horizontal strips for full-page processing
            width, height = pil_image.size
            strip_height = 384  # TrOCR works well with this height
            num_strips = (height + strip_height - 1) // strip_height
            
            print(f"Processing image in {num_strips} horizontal strip(s)")
            
            for i in range(num_strips):
                y_start = i * strip_height
                y_end = min((i + 1) * strip_height, height)
                
                strip = pil_image.crop((0, y_start, width, y_end))
                
                try:
                    text = process_image_with_trocr(strip)
                    if text.strip():
                        extracted_texts.append(text)
                        print(f"Strip {i+1}/{num_strips}: '{text[:50]}...'")
                except Exception as e:
                    print(f"Error processing strip {i+1}: {str(e)}")
        
        # Join with newlines for line-based, spaces for strip-based
        best_text = '\n'.join(extracted_texts) if text_lines and len(text_lines) > 1 else ' '.join(extracted_texts)
        
        print(f"OCR completed: {len(best_text)} chars extracted")
        
        if not best_text or len(best_text.strip()) < 10:
            print("WARNING: Very little text extracted. Image may be of poor quality or empty.")
            return "Error: Could not extract meaningful text. Please ensure image is clear and contains readable text."
        
        # Clean the extracted text
        result = clean_ocr_text(best_text)
        print(f"Extracted {len(result)} characters (cleaned from {len(best_text)})")
        print(f"Preview: {result[:200]}...")
        
        return result
    
    except Exception as e:
        error_msg = f"OCR extraction failed: {str(e)}"
        print(error_msg)
        print(f"Image path: {image_path}")
        print(f"Image exists: {os.path.exists(image_path)}")
        return f"Error: {error_msg}"

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file.
    
    Note: For scanned PDFs, this converts pages to images and applies OCR.
    """
    try:
        from pdf2image import convert_from_path
        
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        
        extracted_text = []
        
        # Extract text from each page
        for i, image in enumerate(images):
            # Save image temporarily
            temp_image_path = f"temp_page_{i}.png"
            image.save(temp_image_path, 'PNG')
            
            # Extract text
            page_text = extract_text_from_image(temp_image_path)
            extracted_text.append(f"--- Page {i+1} ---\n{page_text}")
            
            # Clean up temporary image
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        
        return "\n\n".join(extracted_text)
    
    except ImportError:
        return "Error: pdf2image library not installed. Install with: pip install pdf2image"
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def process_uploaded_file(file_path):
    """
    Process uploaded file and extract text based on file type.
    
    Args:
        file_path: Path to uploaded file
        
    Returns:
        Extracted text or error message
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.png', '.jpg', '.jpeg']:
            return extract_text_from_image(file_path)
        elif file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        else:
            return f"Error: Unsupported file format {file_extension}"
    
    except Exception as e:
        return f"Error processing file: {str(e)}"
