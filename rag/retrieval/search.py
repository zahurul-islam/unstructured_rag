"""
Vector search module.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Union

from app.config import config
from rag.processing.chunker import Chunk
from rag.processing.embedder import get_embedder
from rag.retrieval.milvus_client import get_milvus_client

# Configure logging
logger = logging.getLogger(__name__)


class SearchResult:
    """
    Represents a search result with text content, metadata, and similarity score.
    """
    
    def __init__(
        self,
        text: str,
        metadata: Dict[str, Any],
        score: float,
    ):
        """
        Initialize a search result.
        
        Args:
            text: Text content
            metadata: Metadata
            score: Similarity score
        """
        self.text = text
        self.metadata = metadata
        self.score = score
    
    def __str__(self) -> str:
        return f"SearchResult(score={self.score:.4f}, doc={self.metadata.get('document_name', 'unknown')})"
    
    def __repr__(self) -> str:
        return self.__str__()


def search_documents(
    query: str,
    top_k: int = None,
    similarity_threshold: float = None,
    document_ids: List[str] = None,
) -> List[SearchResult]:
    """
    Search for documents similar to the query.
    
    Args:
        query: Query text
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score threshold
        document_ids: Optional list of document IDs to limit search to
        
    Returns:
        List of SearchResult objects
    """
    # Use configuration if not specified
    top_k = top_k or config.retrieval.top_k
    similarity_threshold = similarity_threshold or config.retrieval.similarity_threshold
    
    # Start timer
    start_time = time.time()
    
    # Get embedder and Milvus client
    embedder = get_embedder()
    milvus_client = get_milvus_client()
    
    # Generate query embedding
    query_embedding = embedder.embed_text(query)
    
    # Create filter expression if document_ids is provided
    expr = None
    if document_ids:
        document_ids_str = ",".join([f'"{doc_id}"' for doc_id in document_ids])
        expr = f"document_id in [{document_ids_str}]"
    
    # Search Milvus
    results = milvus_client.search(
        query_embedding=query_embedding,
        top_k=top_k,
        expr=expr,
        output_fields=["document_id", "document_name", "chunk_index", "text", "metadata"],
    )
    
    # Filter by similarity threshold and convert to SearchResult objects
    search_results = []
    
    for result in results:
        if result["score"] >= similarity_threshold:
            search_result = SearchResult(
                text=result["text"],
                metadata={
                    "document_id": result["document_id"],
                    "document_name": result["document_name"],
                    "chunk_index": result["chunk_index"],
                    **result.get("metadata", {})
                },
                score=result["score"],
            )
            search_results.append(search_result)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    logger.info(f"Search completed in {elapsed_time:.2f}s, found {len(search_results)} results")
    
    return search_results
