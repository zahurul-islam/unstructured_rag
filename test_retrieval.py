
"""
Test script to debug retrieval in the RAG system.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import RAG components
from rag.retrieval.search import search_documents
from rag.processing.embedder import get_embedder

def test_retrieval(query, top_k=10, similarity_threshold=0.1):
    """
    Test retrieval with a query.
    """
    logger.info(f"Testing retrieval for query: '{query}'")
    
    # Set lower similarity threshold to see more results
    results = search_documents(
        query=query,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    logger.info(f"Found {len(results)} results with similarity threshold {similarity_threshold}")
    
    if not results:
        logger.warning("No results found!")
        return
    
    # Print results
    for i, result in enumerate(results):
        logger.info(f"Result {i+1} (score: {result.score:.4f})")
        logger.info(f"Document: {result.metadata.get('document_name')}")
        logger.info(f"Text: {result.text[:200]}...")
        logger.info("-" * 80)

if __name__ == "__main__":
    # Test with a few different queries
    test_retrieval("what is the total amount?")
    test_retrieval("what is the invoice number?")
    test_retrieval("what is the date?")
    test_retrieval("who is the vendor?")
    test_retrieval("tell me about this document")
