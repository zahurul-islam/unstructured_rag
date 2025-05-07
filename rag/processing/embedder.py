"""
Embedding generation module.
"""

import logging
from typing import List, Dict, Any, Union
import numpy as np

from app.config import config
from rag.processing.chunker import Chunk

# Configure logging
logger = logging.getLogger(__name__)


class Embedder:
    """
    Text embedding generator using a pre-trained model.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedder with a pre-trained model.
        
        Args:
            model_name: Name of the pre-trained model to use
        """
        self.model_name = model_name or config.embedding.model_name
        self.model = None
        self.dimension = config.embedding.dimension
        
        # Initialize the model
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Update the embedding dimension based on the model
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding dimension: {self.dimension}")
        
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as a list of floats
        """
        if not self.model:
            raise ValueError("Embedding model not initialized")
        
        # Generate embedding
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise ValueError("Embedding model not initialized")
        
        # Generate embeddings in batch
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of Chunk objects
            
        Returns:
            List of Chunk objects with embeddings added
        """
        if not chunks:
            return []
        
        # Extract texts
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]
        
        return chunks


# Global embedder instance
_embedder = None


def get_embedder() -> Embedder:
    """
    Get the global embedder instance.
    
    Returns:
        Embedder instance
    """
    global _embedder
    
    if _embedder is None:
        _embedder = Embedder()
    
    return _embedder
