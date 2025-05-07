"""
Query handling endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import config

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    """Query request model."""

    query: str = Field(..., description="The user's query text")
    top_k: Optional[int] = Field(None, description="Number of results to retrieve")
    document_ids: Optional[List[str]] = Field(
        None, description="Optional list of document IDs to limit search to"
    )
    similarity_threshold: Optional[float] = Field(
        None, description="Minimum similarity score threshold"
    )


class QuerySource(BaseModel):
    """Source information for a retrieved chunk."""

    document_id: str
    document_name: str
    chunk_index: int
    similarity: float


class QueryResult(BaseModel):
    """Query result model."""

    answer: str
    sources: List[QuerySource]
    processing_time_ms: float


@router.post("/query", response_model=QueryResult)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with natural language.
    """
    try:
        import time
        from rag.retrieval.search import search_documents
        from rag.generation.response import generate_response
        
        # Start timing
        start_time = time.time()
        
        # Set parameters
        top_k = request.top_k or config.retrieval.top_k
        similarity_threshold = request.similarity_threshold or config.retrieval.similarity_threshold
        
        # Search for relevant document chunks
        results = search_documents(
            request.query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            document_ids=request.document_ids
        )
        
        # If no results found
        if not results:
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return QueryResult(
                answer="I couldn't find any relevant information to answer your query in the documents. Please try rephrasing your question or uploading more documents.",
                sources=[],
                processing_time_ms=processing_time
            )
        
        # Generate response
        answer = generate_response(request.query, results)
        
        # Format sources
        sources = []
        for chunk in results:
            sources.append(
                QuerySource(
                    document_id=chunk.metadata.get("document_id", "unknown"),
                    document_name=chunk.metadata.get("document_name", "unknown"),
                    chunk_index=chunk.metadata.get("chunk_index", 0),
                    similarity=chunk.score
                )
            )
        
        # Calculate processing time
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return QueryResult(
            answer=answer,
            sources=sources,
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
