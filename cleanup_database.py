
"""
Script to clean up the Milvus database and remove all document files.
"""

import os
import sys
import logging
import shutil
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clean_vector_database():
    """
    Delete all vectors from the Milvus collection.
    """
    try:
        # Import required modules
        from app.config import config
        from rag.retrieval.milvus_client import get_milvus_client
        from pymilvus import Collection
        
        # Get Milvus client
        logger.info("Connecting to Milvus...")
        milvus_client = get_milvus_client()
        
        # Get collection and check if it exists
        collection_name = config.milvus.collection
        logger.info(f"Dropping collection: {collection_name}")
        
        # Delete all entities in the collection
        expr = "" # Empty expression means all entities
        result = milvus_client.delete(collection_name, expr)
        
        logger.info(f"Deleted all entities from collection {collection_name}")
        
        # Flush the collection to ensure changes are persisted
        logger.info("Flushing collection...")
        milvus_client.collection.flush()
        
        return True
    
    except Exception as e:
        logger.error(f"Error cleaning vector database: {str(e)}")
        return False

def remove_document_files():
    """
    Remove all document files and metadata from the documents directory.
    """
    try:
        from app.config import config
        
        documents_dir = config.app.documents_dir
        logger.info(f"Cleaning documents directory: {documents_dir}")
        
        # Count deleted files
        deleted_count = 0
        
        # List all files in the documents directory
        for filename in os.listdir(documents_dir):
            file_path = os.path.join(documents_dir, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Remove the file
            os.remove(file_path)
            deleted_count += 1
            
        logger.info(f"Removed {deleted_count} files from documents directory")
        
        return True
    
    except Exception as e:
        logger.error(f"Error removing document files: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting database cleanup...")
    
    # Clean vector database
    db_result = clean_vector_database()
    
    # Remove document files
    files_result = remove_document_files()
    
    if db_result and files_result:
        print("Successfully cleaned up the database and removed all document files.")
    else:
        print("Cleanup completed with some errors. Check the logs for details.")
