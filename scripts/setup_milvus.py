#!/usr/bin/env python
"""
Setup script for Milvus vector database.
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import config
from rag.retrieval.milvus_client import MilvusClient


def setup_milvus():
    """Set up Milvus collection and index."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Setting up Milvus collection")
    
    try:
        # Create Milvus client (this will automatically create the collection if it doesn't exist)
        client = MilvusClient(
            host=config.milvus.host,
            port=config.milvus.port,
            collection_name=config.milvus.collection,
        )
        
        # List collections
        collections = client.list_collections()
        logger.info(f"Available collections: {collections}")
        
        # Count entities
        count = client.count()
        logger.info(f"Collection '{config.milvus.collection}' contains {count} entities")
        
        logger.info("Milvus setup completed successfully")
    
    except Exception as e:
        logger.error(f"Error setting up Milvus: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    setup_milvus()
