
"""
Enhanced PDF document loader with better OCR.
"""

import os
import logging
from typing import Dict, Tuple, Any
import tempfile

# Configure logging
logger = logging.getLogger(__name__)


def load_pdf_with_advanced_ocr(file_path: str, dpi: int = 300) -> Tuple[str, Dict[str, Any]]:
    """
    Load a PDF using advanced OCR settings as a last resort.
    
    Args:
        file_path: Path to the PDF file
        dpi: DPI for image conversion (higher = better quality but slower)
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
        from PIL import Image
        
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
            
            # Create PDF-specific metadata
            metadata = {
                "page_count": len(images),
                "source_type": "pdf",
                "extraction_method": "advanced_ocr"
            }
            
            return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading PDF with advanced OCR: {str(e)}")
        
        # Return empty text with error metadata as last resort
        return "", {
            "source_type": "pdf",
            "extraction_error": str(e),
            "extraction_success": False
        }
