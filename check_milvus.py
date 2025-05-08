
"""
Script to check the status of the Milvus collection.
"""

import os
import sys
import logging
from pymilvus import connections, utility, Collection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_milvus_collection():
    """
    Check the status of the Milvus collection.
    """
    try:
        # Import config
        from app.config import config
        
        # Connect to Milvus
        host = config.milvus.host
        port = config.milvus.port
        collection_name = config.milvus.collection
        
        logger.info(f"Connecting to Milvus at {host}:{port}")
        connections.connect(
            alias="default",
            host=host,
            port=port,
        )
        
        # Check if collection exists
        if utility.has_collection(collection_name):
            logger.info(f"Collection '{collection_name}' exists")
            
            # Load collection
            collection = Collection(collection_name)
            collection.load()
            
            # Get entity count
            entity_count = collection.num_entities
            logger.info(f"Collection '{collection_name}' contains {entity_count} entities")
            
            # List all collections
            all_collections = utility.list_collections()
            logger.info(f"Available collections: {all_collections}")
            
            return True
        else:
            logger.info(f"Collection '{collection_name}' does not exist")
            return False
        
    except Exception as e:
        logger.error(f"Error checking Milvus collection: {str(e)}")
        return False

def check_documents_directory():
    """
    Check the contents of the documents directory.
    """
    try:
        from app.config import config
        
        documents_dir = config.app.documents_dir
        logger.info(f"Checking documents directory: {documents_dir}")
        
        # Count files
        file_count = 0
        
        # List all files in the documents directory
        for filename in os.listdir(documents_dir):
            file_path = os.path.join(documents_dir, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            file_count += 1
            
        logger.info(f"Documents directory contains {file_count} files")
        
        return True
    
    except Exception as e:
        logger.error(f"Error checking documents directory: {str(e)}")
        return False

if __name__ == "__main__":
    print("Checking Milvus collection and documents directory...")
    
    # Check Milvus collection
    milvus_result = check_milvus_collection()
    
    # Check documents directory
    docs_result = check_documents_directory()
    
    if milvus_result and docs_result:
        print("Check completed successfully.")
    else:
        print("Check completed with some errors. See logs for details.")
