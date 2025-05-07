"""
PDF document loader.
"""

import os
import logging
from typing import Dict, Tuple, Any
import tempfile

# Configure logging
logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a PDF document and extract its text and metadata.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        # Use langchain's PDF loader which internally uses unstructured-io
        from langchain_community.document_loaders import UnstructuredPDFLoader
        
        # Load the PDF document
        loader = UnstructuredPDFLoader(file_path)
        documents = loader.load()
        
        # Combine text from all pages
        text = " ".join([doc.page_content for doc in documents])
        
        # Create PDF-specific metadata
        metadata = {
            "page_count": len(documents),
            "source_type": "pdf"
        }
        
        return text, metadata
    
    except ImportError:
        logger.warning("UnstructuredPDFLoader not available. Falling back to PyPDF.")
        return load_pdf_with_pypdf(file_path)
    
    except Exception as e:
        logger.error(f"Error loading PDF with UnstructuredPDFLoader: {str(e)}")
        logger.info("Falling back to PyPDF")
        return load_pdf_with_pypdf(file_path)


def load_pdf_with_pypdf(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Fallback method to load a PDF using PyPDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        import pypdf
        
        # Open the PDF
        with open(file_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            
            # Extract text from each page
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + " "
            
            # Extract metadata
            pdf_info = pdf_reader.metadata
            
            # Create PDF-specific metadata
            metadata = {
                "page_count": len(pdf_reader.pages),
                "source_type": "pdf"
            }
            
            # Add PDF document info if available
            if pdf_info:
                if pdf_info.title:
                    metadata["title"] = pdf_info.title
                if pdf_info.author:
                    metadata["author"] = pdf_info.author
                if pdf_info.subject:
                    metadata["subject"] = pdf_info.subject
                if pdf_info.creator:
                    metadata["creator"] = pdf_info.creator
            
            return text, metadata
    
    except ImportError:
        logger.error("PyPDF not available. Falling back to OCR.")
        return load_pdf_with_ocr(file_path)
    
    except Exception as e:
        logger.error(f"Error loading PDF with PyPDF: {str(e)}")
        logger.info("Falling back to OCR")
        return load_pdf_with_ocr(file_path)


def load_pdf_with_ocr(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a PDF using OCR as a last resort.
    
    Args:
        file_path: Path to the PDF file
        
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
            # Convert PDF to images
            images = convert_from_path(file_path)
            
            # Extract text from each page
            text = ""
            for i, image in enumerate(images):
                # Save the image
                image_path = os.path.join(temp_dir, f"page_{i}.png")
                image.save(image_path, "PNG")
                
                # Extract text from the image
                page_text = pytesseract.image_to_string(Image.open(image_path))
                text += page_text + " "
            
            # Create PDF-specific metadata
            metadata = {
                "page_count": len(images),
                "source_type": "pdf",
                "extraction_method": "ocr"
            }
            
            return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading PDF with OCR: {str(e)}")
        
        # Return empty text with error metadata as last resort
        return "", {
            "source_type": "pdf",
            "extraction_error": str(e),
            "extraction_success": False
        }
