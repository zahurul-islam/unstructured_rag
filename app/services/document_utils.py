"""
Document utility functions.
"""

import os
import json
import logging

from app.config import config

# Configure logging
logger = logging.getLogger(__name__)


def update_document_status(doc_id: str, status: str, message: str = ""):
    """
    Update document processing status.
    
    Args:
        doc_id: Document ID
        status: New status
        message: Optional status message
    """
    metadata_path = os.path.join(config.app.documents_dir, f"{doc_id}.metadata.json")
    
    try:
        with open(metadata_path, "r") as f:
            document = json.load(f)
        
        document["status"] = status
        
        with open(metadata_path, "w") as f:
            json.dump(document, f, indent=2)
    except Exception as e:
        # Log error but don't raise
        logger.error(f"Failed to update document status: {str(e)}")
