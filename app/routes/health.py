"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import config

# Import services
from rag.retrieval.milvus_client import get_milvus_client

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    details: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the API and its dependencies.
    """
    health_details = {
        "milvus": check_milvus_health(),
        "embedding_model": check_embedding_model(),
        "llm": check_llm_configuration(),
    }

    # Determine overall status based on component statuses
    overall_status = "healthy"
    for component, status in health_details.items():
        if status["status"] != "healthy":
            overall_status = "degraded"
            break

    return HealthResponse(
        status=overall_status,
        version="0.1.0",
        details=health_details,
    )


def check_milvus_health() -> dict:
    """Check Milvus connection and status."""
    try:
        # Get Milvus client
        client = get_milvus_client()
        
        # Check connection by listing collections
        collections = client.list_collections()
        
        return {
            "status": "healthy",
            "message": f"Connected to Milvus at {config.milvus.host}:{config.milvus.port}",
            "collections": collections,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Failed to connect to Milvus: {str(e)}",
        }


def check_embedding_model() -> dict:
    """Check embedding model availability."""
    try:
        # Import here to avoid circular imports
        from rag.processing.embedder import get_embedder
        
        # Check if embedder can be initialized
        embedder = get_embedder()
        
        return {
            "status": "healthy",
            "message": f"Embedding model '{config.embedding.model_name}' is available",
            "model": config.embedding.model_name,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Failed to initialize embedding model: {str(e)}",
            "model": config.embedding.model_name,
        }


def check_llm_configuration() -> dict:
    """Check LLM configuration."""
    if not config.llm.api_key:
        return {
            "status": "unhealthy",
            "message": "DeepSeek API key is not configured",
            "model": config.llm.model_name,
        }
    
    try:
        # Import here to avoid circular imports
        from rag.generation.llm import get_llm
        
        # Try to initialize LLM (this won't make an API call)
        llm = get_llm()
        
        return {
            "status": "healthy",
            "message": f"LLM model '{config.llm.model_name}' is configured",
            "model": config.llm.model_name,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Failed to initialize LLM: {str(e)}",
            "model": config.llm.model_name,
        }
