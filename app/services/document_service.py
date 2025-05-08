"""
Document processing service.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple

from app.config import config
from app.services.document_utils import update_document_status

# Configure logging
logger = logging.getLogger(__name__)


async def process_document(doc_id: str, file_path: str, file_extension: str):
    """
    Process a document and store its chunks in the vector database.
    
    Args:
        doc_id: Document ID
        file_path: Path to the document file
        file_extension: File extension
    """
    try:
        # Import here to avoid circular imports
        from rag.data_ingestion.loader import load_document
        from rag.processing.chunker import chunk_text
        from rag.processing.embedder import get_embedder
        from rag.retrieval.milvus_client import store_chunks
        
        # Update document status
        update_document_status(doc_id, "processing", "Loading document")
        
        # Load document
        text, metadata = load_document(file_path)
        
        if not text:
            update_document_status(doc_id, "error", "Failed to extract text from document")
            logger.error(f"No text extracted from document: {file_path}")
            return
        
        # Update document status
        update_document_status(doc_id, "processing", "Chunking text")
        
        # Add document ID to metadata
        metadata["document_id"] = doc_id
        
        # Chunk text with better strategy
        chunks = chunk_text(
            text=text,
            chunk_size=config.chunking.chunk_size,
            chunk_overlap=config.chunking.chunk_overlap,
            metadata=metadata,
            strategy="sentence",  # Use sentence-based chunking for better context preservation
        )
        
        if not chunks:
            update_document_status(doc_id, "error", "Failed to create chunks from document")
            logger.error(f"No chunks created from document: {file_path}")
            return
        
        # Update document status
        update_document_status(doc_id, "processing", "Generating embeddings")
        
        # Get embedder
        embedder = get_embedder()
        
        # Get document name from metadata
        document_name = metadata.get("file_name", os.path.basename(file_path))
        
        # Store chunks in vector database
        store_chunks(chunks, doc_id, document_name, embedder)
        
        # Update document status
        update_document_status(doc_id, "completed", f"Processed {len(chunks)} chunks")
        
        # Update document metadata with chunk count
        metadata_path = os.path.join(config.app.documents_dir, f"{doc_id}.metadata.json")
        
        try:
            import json
            
            with open(metadata_path, "r") as f:
                metadata_json = json.load(f)
            
            metadata_json["chunk_count"] = len(chunks)
            
            with open(metadata_path, "w") as f:
                json.dump(metadata_json, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
        
        logger.info(f"Document processed successfully: {file_path}")
    
    except Exception as e:
        # Update document status
        update_document_status(doc_id, "error", f"Error: {str(e)}")
        logger.error(f"Error processing document {doc_id}: {str(e)}")
