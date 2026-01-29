"""OCR processor using Tesseract for text extraction from images."""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
import os
from config import Config

# Set Tesseract command path
if Config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def preprocess_image(image_path):
    """
    Preprocess image to improve OCR accuracy.
    
    Steps:
    1. Convert to grayscale
    2. Apply noise reduction
    3. Enhance contrast
    4. Apply thresholding
    """
    try:
        # Read image with OpenCV
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError("Failed to load image")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Apply adaptive thresholding for better text contrast
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Save preprocessed image temporarily
        preprocessed_path = image_path.replace('.', '_preprocessed.')
        cv2.imwrite(preprocessed_path, thresh)
        
        return preprocessed_path
    
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        # Return original image path if preprocessing fails
        return image_path

def extract_text_from_image(image_path):
    """
    Extract text from image using Tesseract OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        # Preprocess image
        preprocessed_path = preprocess_image(image_path)
        
        # Open image with PIL
        image = Image.open(preprocessed_path)
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6'  # LSTM OCR engine, assume uniform block of text
        
        # Extract text
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Clean up preprocessed image if it's different from original
        if preprocessed_path != image_path and os.path.exists(preprocessed_path):
            os.remove(preprocessed_path)
        
        # Clean and return text
        return text.strip()
    
    except Exception as e:
        error_msg = f"OCR extraction failed: {str(e)}"
        print(error_msg)
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
