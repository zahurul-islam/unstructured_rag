
"""
Test script to extract text from a PDF using OCR.
"""

import os
import sys
import logging
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_with_ocr(file_path, dpi=300):
    """
    Extract text from a PDF using OCR with higher DPI and better settings.
    
    Args:
        file_path: Path to the PDF file
        dpi: DPI for image conversion (higher = better quality but slower)
    """
    logger.info(f"Extracting text from PDF with OCR: {file_path}")
    
    # Create a temporary directory for the images
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert PDF to images with higher DPI
        logger.info(f"Converting PDF to images with DPI={dpi}")
        images = convert_from_path(file_path, dpi=dpi)
        
        # Extract text from each page
        text = ""
        
        for i, image in enumerate(images):
            # Save the image
            image_path = os.path.join(temp_dir, f"page_{i}.png")
            image.save(image_path, "PNG")
            
            logger.info(f"Extracting text from page {i+1}/{len(images)}")
            
            # Extract text from the image with better OCR settings
            page_text = pytesseract.image_to_string(
                Image.open(image_path),
                lang='deu+eng',  # Use both German and English language models
                config='--psm 1 --oem 3'  # PSM 1: Auto-detect, OEM 3: Default engine mode
            )
            
            text += page_text + "\n\n"
        
        return text

if __name__ == "__main__":
    # Test with one PDF file
    pdf_files = [
        "/home/zahurul/Documents/work/playground/unstructured_rag/data/documents/b774f9ab-37b3-4611-96a3-847b15ee202d.pdf",
        "/home/zahurul/Documents/work/playground/unstructured_rag/data/documents/0e614e6f-32f4-4a91-8fa7-5b26ff659d2e.pdf"
    ]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            logger.info(f"Processing PDF: {pdf_file}")
            
            # Extract text with OCR
            text = extract_text_with_ocr(pdf_file, dpi=300)
            
            # Print the extracted text
            logger.info("Extracted Text:")
            print("=" * 80)
            print(text)
            print("=" * 80)
            
            # Save the extracted text to a file
            output_file = os.path.splitext(pdf_file)[0] + ".txt"
            with open(output_file, "w") as f:
                f.write(text)
            
            logger.info(f"Text saved to: {output_file}")
        else:
            logger.error(f"PDF file not found: {pdf_file}")
