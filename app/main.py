"""
Main FastAPI application module.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import config

# Import routes
from app.routes import documents, query, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.app.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Unstructured RAG API",
    description="API for Retrieval-Augmented Generation with unstructured data",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(query.router, tags=["Query"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute actions on application startup."""
    logger.info("Starting Unstructured RAG API")
    try:
        # Import here to avoid circular imports
        from rag.retrieval.milvus_client import get_milvus_client

        # Check Milvus connection
        milvus_client = get_milvus_client()
        logger.info(f"Connected to Milvus at {config.milvus.host}:{config.milvus.port}")
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {str(e)}")
        # Don't raise exception to allow app to start even if Milvus is not available


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute actions on application shutdown."""
    logger.info("Shutting down Unstructured RAG API")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config.app.host,
        port=config.app.port,
        reload=True,
    )
