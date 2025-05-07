"""
Response generation module.
"""

import logging
from typing import List, Dict, Any, Optional

from app.config import config
from rag.retrieval.search import SearchResult
from rag.generation.llm import get_llm
from rag.generation.prompts import RAG_PROMPT_TEMPLATE

# Configure logging
logger = logging.getLogger(__name__)


def generate_response(query: str, results: List[SearchResult]) -> str:
    """
    Generate a response based on search results.
    
    Args:
        query: User query
        results: List of search results
        
    Returns:
        Generated response
    """
    # Get LLM
    llm = get_llm()
    
    # Prepare context from search results
    context = prepare_context(results)
    
    # Generate response
    input_variables = {
        "query": query,
        "context": context,
    }
    
    try:
        response = llm.generate_with_chain(
            template=RAG_PROMPT_TEMPLATE,
            input_variables=input_variables,
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"Error generating response: {str(e)}"


def prepare_context(results: List[SearchResult]) -> str:
    """
    Prepare context from search results.
    
    Args:
        results: List of search results
        
    Returns:
        Context string
    """
    if not results:
        return "No relevant information found."
    
    # Sort results by score (highest first)
    sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
    
    # Build context
    context_parts = []
    
    for i, result in enumerate(sorted_results):
        # Add source information
        source_info = f"[Document: {result.metadata.get('document_name', 'Unknown')}]"
        
        # Add context with source
        context_part = f"--- SOURCE {i+1}: {source_info} ---\n{result.text}\n"
        context_parts.append(context_part)
    
    return "\n".join(context_parts)
