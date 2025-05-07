"""
Document loader module for handling various file types.
"""

import os
import logging
from typing import Dict, Tuple, Any
import mimetypes

# Configure logging
logger = logging.getLogger(__name__)


def load_document(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a document from a file path and extract its text and metadata.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    # Get file extension and determine file type
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Get mimetype
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Basic metadata common to all files
    metadata = {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "file_extension": file_extension,
        "file_size": file_size,
        "mime_type": mime_type or "application/octet-stream",
    }
    
    # Load document based on file extension
    if file_extension == ".pdf":
        from rag.data_ingestion.pdf_loader import load_pdf
        text, pdf_metadata = load_pdf(file_path)
        metadata.update(pdf_metadata)
    
    elif file_extension in [".docx", ".doc"]:
        from rag.data_ingestion.docx_loader import load_docx
        text, docx_metadata = load_docx(file_path)
        metadata.update(docx_metadata)
    
    elif file_extension in [".txt", ".md", ".rtf"]:
        from rag.data_ingestion.text_loader import load_text
        text, text_metadata = load_text(file_path)
        metadata.update(text_metadata)
    
    elif file_extension in [".html", ".htm"]:
        from rag.data_ingestion.html_loader import load_html
        text, html_metadata = load_html(file_path)
        metadata.update(html_metadata)
    
    elif file_extension == ".csv":
        from rag.data_ingestion.csv_loader import load_csv
        text, csv_metadata = load_csv(file_path)
        metadata.update(csv_metadata)
    
    elif file_extension == ".json":
        from rag.data_ingestion.json_loader import load_json
        text, json_metadata = load_json(file_path)
        metadata.update(json_metadata)
    
    else:
        # Default to text loader for unknown file types
        from rag.data_ingestion.text_loader import load_text
        text, text_metadata = load_text(file_path)
        metadata.update(text_metadata)
        logger.warning(f"Unsupported file extension: {file_extension}. Using text loader.")
    
    logger.info(f"Successfully loaded document: {file_path}")
    return text, metadata
