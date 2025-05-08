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

    # Group results by document to avoid repetition
    doc_groups = {}
    for result in sorted_results:
        doc_id = result.metadata.get('document_id', 'unknown')
        if doc_id not in doc_groups:
            doc_groups[doc_id] = {
                'name': result.metadata.get('document_name', 'Unknown'),
                'results': []
            }
        doc_groups[doc_id]['results'].append(result)

    # Build context
    context_parts = []

    # Process each document group
    for i, (doc_id, group) in enumerate(doc_groups.items()):
        # Get document name and clean it up
        doc_name = group['name']

        # Remove file extension if present
        if '.' in doc_name:
            doc_name = doc_name.rsplit('.', 1)[0]

        # Handle special document names
        if 'wikipedia' in doc_name.lower() and 'language model' in doc_name.lower():
            doc_name = "Wikipedia - Large Language Models"
        elif 'llm_info' in doc_name.lower() or 'llm-info' in doc_name.lower():
            doc_name = "LLM Information Guide"
        # Clean up UUID-like names
        elif len(doc_name) > 8 and '-' in doc_name:
            doc_name = f"Document {i+1}"

        # Add source information with clear formatting
        source_info = f"DOCUMENT {i+1}: {doc_name}"

        # Combine text from all results for this document
        doc_text = "\n\n".join([r.text for r in group['results']])

        # Add context with source
        context_part = f"=== {source_info} ===\n{doc_text}\n"
        context_parts.append(context_part)

    return "\n\n".join(context_parts)
