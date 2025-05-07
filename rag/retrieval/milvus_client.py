"""
Milvus vector database client.
"""

import logging
from typing import List, Dict, Any, Optional, Union
import time

from app.config import config
from rag.processing.chunker import Chunk
from rag.processing.embedder import Embedder

# Configure logging
logger = logging.getLogger(__name__)


class MilvusClient:
    """
    Client for Milvus vector database operations.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = None,
    ):
        """
        Initialize the Milvus client.
        
        Args:
            host: Milvus server host
            port: Milvus server port
            collection_name: Name of the collection to use
        """
        self.host = host or config.milvus.host
        self.port = port or config.milvus.port
        self.collection_name = collection_name or config.milvus.collection
        self.client = None
        self.collection = None
        self.dimension = config.embedding.dimension
        
        # Connect to Milvus
        self._connect()
    
    def _connect(self):
        """Connect to Milvus server and initialize collection."""
        try:
            from pymilvus import connections, Collection, utility
            
            # Connect to Milvus server
            logger.info(f"Connecting to Milvus at {self.host}:{self.port}")
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
            )
            
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' exists")
                self.collection = Collection(self.collection_name)
                self.collection.load()
            else:
                logger.info(f"Collection '{self.collection_name}' does not exist")
                self._create_collection()
        
        except Exception as e:
            logger.error(f"Error connecting to Milvus: {str(e)}")
            raise
    
    def _create_collection(self):
        """Create the collection if it doesn't exist."""
        try:
            from pymilvus import Collection, DataType, FieldSchema, CollectionSchema
            
            # Define collection schema
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="chunk_index", dtype=DataType.INT64),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            ]
            
            schema = CollectionSchema(fields)
            
            # Create collection
            logger.info(f"Creating collection: {self.collection_name}")
            self.collection = Collection(
                name=self.collection_name,
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
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params,
            )
            
            # Load collection into memory
            self.collection.load()
        
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def insert(self, chunks: List[Dict[str, Any]]):
        """
        Insert chunks into the collection.
        
        Args:
            chunks: List of chunk dictionaries
        """
        if not self.collection:
            self._connect()
        
        try:
            # Insert data
            result = self.collection.insert(chunks)
            logger.info(f"Inserted {result.insert_count} chunks")
            
            # Flush to ensure data is persisted
            self.collection.flush()
            
            return result
        
        except Exception as e:
            logger.error(f"Error inserting chunks: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        expr: str = None,
        output_fields: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            expr: Boolean expression for filtering
            output_fields: Fields to include in the results
            
        Returns:
            List of search results
        """
        if not self.collection:
            self._connect()
        
        try:
            # Default output fields
            if output_fields is None:
                output_fields = ["id", "document_id", "document_name", "chunk_index", "text", "metadata"]
            
            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 64},
            }
            
            # Execute search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=output_fields,
            )
            
            # Format results
            formatted_results = []
            
            for hits in results:
                for hit in hits:
                    result = {
                        "id": hit.id,
                        "score": hit.score,
                    }
                    
                    # Add output fields
                    for field in output_fields:
                        if field != "id":  # ID is already added
                            result[field] = hit.entity.get(field)
                    
                    formatted_results.append(result)
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise
    
    def delete(self, collection_name: str, expr: str):
        """
        Delete entities from a collection.
        
        Args:
            collection_name: Name of the collection
            expr: Boolean expression for filtering entities to delete
        """
        if not self.collection:
            self._connect()
        
        try:
            # Execute delete
            result = self.collection.delete(expr)
            logger.info(f"Deleted {result.delete_count} entities")
            
            # Flush to ensure changes are persisted
            self.collection.flush()
            
            return result
        
        except Exception as e:
            logger.error(f"Error deleting entities: {str(e)}")
            raise
    
    def count(self, expr: str = None) -> int:
        """
        Count the number of entities in the collection.
        
        Args:
            expr: Boolean expression for filtering
            
        Returns:
            Number of entities
        """
        if not self.collection:
            self._connect()
        
        try:
            if expr:
                count = self.collection.query(expr=expr, output_fields=["count(*)"])
                return count[0]["count(*)"]
            else:
                return self.collection.num_entities
        
        except Exception as e:
            logger.error(f"Error counting entities: {str(e)}")
            raise
    
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        try:
            from pymilvus import utility
            
            return utility.list_collections()
        
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise


# Global client instance
_milvus_client = None


def get_milvus_client() -> MilvusClient:
    """
    Get the global Milvus client instance.
    
    Returns:
        MilvusClient instance
    """
    global _milvus_client
    
    if _milvus_client is None:
        _milvus_client = MilvusClient()
    
    return _milvus_client


def store_chunks(chunks: List[Chunk], document_id: str, document_name: str, embedder: Optional[Embedder] = None):
    """
    Store chunks in Milvus.
    
    Args:
        chunks: List of Chunk objects
        document_id: Document ID
        document_name: Document name
        embedder: Embedder instance (optional)
    """
    if not chunks:
        return
    
    # Get embedder if not provided
    if embedder is None:
        from rag.processing.embedder import get_embedder
        embedder = get_embedder()
    
    # Generate embeddings if not already present
    chunks_with_embeddings = []
    for chunk in chunks:
        if chunk.embedding is None:
            chunks_with_embeddings.append(chunk)
    
    if chunks_with_embeddings:
        embedder.embed_chunks(chunks_with_embeddings)
    
    # Prepare data for Milvus
    milvus_data = []
    
    for chunk in chunks:
        # Generate a unique ID for the chunk
        chunk_id = f"{document_id}_{chunk.metadata['chunk_index']}"
        
        # Prepare chunk data
        chunk_data = {
            "id": chunk_id,
            "document_id": document_id,
            "document_name": document_name,
            "chunk_index": chunk.metadata["chunk_index"],
            "text": chunk.text,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding,
        }
        
        milvus_data.append(chunk_data)
    
    # Get Milvus client
    client = get_milvus_client()
    
    # Insert chunks
    client.insert(milvus_data)
