#!/usr/bin/env python
"""
Setup script for Milvus vector database.
"""

import os
import sys
import logging
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import config


def setup_milvus():
    """Set up Milvus collection and index."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Setting up Milvus collection")
    
    # Import here to avoid circular imports
    from pymilvus import connections, Collection, DataType, FieldSchema, CollectionSchema, utility
    
    max_retries = 5
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Connect to Milvus server
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
                try:
                    collection = Collection(collection_name)
                    
                    # Wait for collection to load
                    for load_attempt in range(3):
                        try:
                            logger.info(f"Loading collection (attempt {load_attempt+1}/3)...")
                            collection.load()
                            logger.info(f"Collection '{collection_name}' loaded successfully")
                            break
                        except Exception as e:
                            logger.warning(f"Failed to load collection on attempt {load_attempt+1}: {str(e)}")
                            if load_attempt < 2:  # Wait before retrying
                                time.sleep(5)
                            else:
                                logger.info("Continuing without loading collection")
                except Exception as e:
                    logger.warning(f"Failed to load existing collection: {str(e)}")
                    logger.info("Continuing without loading collection")
            else:
                logger.info(f"Collection '{collection_name}' does not exist")
                
                # Define collection schema
                dimension = config.embedding.dimension
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
                
                # Try to load collection, but don't raise error if it fails
                try:
                    logger.info("Loading collection...")
                    collection.load()
                    logger.info("Collection loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load collection: {str(e)}")
                    logger.info("Continuing without loading collection")
            
            # List collections
            collections = utility.list_collections()
            logger.info(f"Available collections: {collections}")
            
            # Get count if collection exists
            if utility.has_collection(collection_name):
                try:
                    # Try to get count, but don't fail if it doesn't work
                    collection = Collection(collection_name)
                    count = collection.num_entities
                    logger.info(f"Collection '{collection_name}' contains {count} entities")
                except Exception as e:
                    logger.warning(f"Failed to get entity count: {str(e)}")
            
            logger.info("Milvus setup completed successfully")
            return
        
        except Exception as e:
            logger.error(f"Error setting up Milvus (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Milvus setup failed.")
                sys.exit(1)


if __name__ == "__main__":
    setup_milvus()
