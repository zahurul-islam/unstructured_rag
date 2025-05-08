
"""
Script to drop and recreate the Milvus collection.
"""

import os
import sys
import logging
import time
from pymilvus import connections, utility, Collection, FieldSchema, DataType, CollectionSchema
import pymilvus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reset_milvus_collection():
    """
    Drop and recreate the Milvus collection.
    """
    try:
        # Import config
        from app.config import config
        
        # Connect to Milvus
        host = config.milvus.host
        port = config.milvus.port
        collection_name = config.milvus.collection
        dimension = config.embedding.dimension
        
        logger.info(f"Connecting to Milvus at {host}:{port}")
        connections.connect(
            alias="default",
            host=host,
            port=port,
        )
        
        # Check if collection exists
        if utility.has_collection(collection_name):
            logger.info(f"Dropping collection {collection_name}")
            utility.drop_collection(collection_name)
            logger.info(f"Collection {collection_name} dropped")
        
        # Define collection schema
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]
        
        schema = CollectionSchema(fields)
        
        # Create collection
        logger.info(f"Creating collection: {collection_name}")
        collection = Collection(
            name=collection_name,
            schema=schema,
            using="default",
        )
        
        # Create index on the embedding field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64},
        }
        
        logger.info("Creating index on embedding field")
        collection.create_index(
            field_name="embedding",
            index_params=index_params,
        )
        
        # Load collection into memory
        collection.load()
        
        logger.info(f"Collection {collection_name} created successfully")
        
        # List all collections to verify
        all_collections = utility.list_collections()
        logger.info(f"Available collections: {all_collections}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error resetting Milvus collection: {str(e)}")
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
    print("Starting Milvus reset and cleanup...")
    
    # Reset Milvus collection
    milvus_result = reset_milvus_collection()
    
    # Remove document files
    files_result = remove_document_files()
    
    if milvus_result and files_result:
        print("Successfully reset Milvus collection and removed all document files.")
    else:
        print("Reset completed with some errors. Check the logs for details.")
