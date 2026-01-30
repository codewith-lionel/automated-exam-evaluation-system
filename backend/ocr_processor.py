"""OCR processor using Tesseract for text extraction from images."""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
import os
import re
from config import Config

# Set Tesseract command path - MUST be set before any pytesseract calls
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

# Verify Tesseract is accessible
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract OCR version {version} configured at: {Config.TESSERACT_CMD}")
except Exception as e:
    print(f"WARNING: Tesseract configuration issue: {str(e)}")
    print(f"Expected path: {Config.TESSERACT_CMD}")
    print(f"Path exists: {os.path.exists(Config.TESSERACT_CMD) if Config.TESSERACT_CMD else False}")


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


def preprocess_image(image_path):
    """
    Preprocess image to improve OCR accuracy.
    Optimized for handwritten text recognition.
    
    Steps:
    1. Load and upscale image
    2. Convert to grayscale
    3. Apply advanced denoising
    4. Enhance contrast
    5. Adaptive thresholding
    6. Morphological operations
    """
    try:
        # Read image with OpenCV
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError("Failed to load image")
        
        # Get image dimensions
        height, width = img.shape[:2]
        
        # Upscale moderately for better OCR (balanced speed and quality)
        if height < 1200 or width < 1200:
            scale = max(1200/height, 1200/width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            print(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Non-local Means Denoising (better for handwriting)
        gray = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Sharpen the image to make text edges clearer
        kernel_sharpen = np.array([[-1,-1,-1],
                                   [-1, 9,-1],
                                   [-1,-1,-1]])
        gray = cv2.filter2D(gray, -1, kernel_sharpen)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16,16))
        gray = clahe.apply(gray)
        
        # Use adaptive thresholding (better for varying lighting and handwriting)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 21, 10)
        print(f"Applied Gaussian adaptive thresholding")
        
        # Morphological operations to clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Remove small noise
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open, iterations=1)
        
        # Ensure text is black on white background
        if np.mean(thresh) < 127:
            thresh = cv2.bitwise_not(thresh)
        
        # Save preprocessed image
        preprocessed_path = image_path.replace('.', '_preprocessed.')
        cv2.imwrite(preprocessed_path, thresh)
        print(f"Saved preprocessed image: {preprocessed_path}")
        
        return preprocessed_path
    
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return image_path

def extract_text_from_image(image_path):
    """
    Extract text from image using Tesseract OCR.
    Optimized for handwritten text.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        # Verify Tesseract is configured
        if not pytesseract.pytesseract.tesseract_cmd:
            raise Exception("Tesseract path not configured in config.py")
        
        if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            raise Exception(f"Tesseract not found at: {pytesseract.pytesseract.tesseract_cmd}")
        
        # Preprocess image
        print(f"Processing image: {image_path}")
        preprocessed_path = preprocess_image(image_path)
        
        # Open image with PIL
        image = Image.open(preprocessed_path)
        
        # Use optimized OCR configuration for speed and accuracy
        # PSM 3 = Fully automatic page segmentation (best for general use)
        # OEM 1 = LSTM engine (accurate and reasonably fast)
        config = r'--oem 1 --psm 3'
        
        try:
            # Extract text with optimized config
            best_text = pytesseract.image_to_string(image, config=config, lang='eng')
            best_config = config
            
            print(f"OCR completed: {len(best_text)} chars extracted")
                    
        except Exception as e:
            print(f"OCR extraction failed: {str(e)}")
            best_text = ""
            best_config = config
        
        # Clean up preprocessed image
        if preprocessed_path != image_path and os.path.exists(preprocessed_path):
            os.remove(preprocessed_path)
        
        if not best_text or len(best_text.strip()) < 10:
            print("WARNING: Very little text extracted. Image may be of poor quality or empty.")
            return "Error: Could not extract meaningful text. Please ensure image is clear and contains readable text."
        
        # Clean the extracted text
        result = clean_ocr_text(best_text)
        print(f"Best config: {best_config}")
        print(f"Extracted {len(result)} characters (cleaned from {len(best_text)})")
        print(f"Preview: {result[:200]}...")
        
        return result
    
    except Exception as e:
        error_msg = f"OCR extraction failed: {str(e)}"
        print(error_msg)
        print(f"Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
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
