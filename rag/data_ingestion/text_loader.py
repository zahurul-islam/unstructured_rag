"""
Text file loader for plain text files.
"""

import os
import logging
from typing import Dict, Tuple, Any
import chardet

# Configure logging
logger = logging.getLogger(__name__)


def load_text(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a text document and extract its content and metadata.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        # Read file as binary first to detect encoding
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            
            # Detect encoding
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            
            # Decode using detected encoding
            text = raw_data.decode(encoding)
        
        # Count lines
        line_count = text.count('\n') + 1
        
        # Get word count (approximate)
        word_count = len(text.split())
        
        # Create text-specific metadata
        metadata = {
            "line_count": line_count,
            "word_count": word_count,
            "source_type": "text",
            "encoding": encoding,
            "encoding_confidence": confidence
        }
        
        return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading text file: {str(e)}")
        
        # Return empty text with error metadata
        return "", {
            "source_type": "text",
            "extraction_error": str(e),
            "extraction_success": False
        }
