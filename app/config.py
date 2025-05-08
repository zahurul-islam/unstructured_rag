"""
Configuration module for the RAG application.
Load settings from environment variables and provide defaults.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(ROOT_DIR / ".env")


class MilvusConfig(BaseModel):
    """Milvus vector database configuration."""

    host: str = Field(default=os.getenv("MILVUS_HOST", "localhost"))
    port: int = Field(default=int(os.getenv("MILVUS_PORT", 19530)))
    collection: str = Field(default=os.getenv("MILVUS_COLLECTION", "unstructured_rag"))


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""

    model_name: str = Field(
        default=os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )
    dimension: int = Field(default=384)  # Default for all-MiniLM-L6-v2


class LLMConfig(BaseModel):
    """LLM configuration for DeepSeek model."""

    api_key: Optional[str] = Field(default=os.getenv("DEEPSEEK_API_KEY"))
    model_name: str = Field(default=os.getenv("LLM_MODEL", "deepseek/deepseek-r1-zero:free"))
    use_gpu: bool = Field(default=os.getenv("USE_GPU", "true").lower() == "true")
    gpu_device: int = Field(default=int(os.getenv("GPU_DEVICE", 0)))
    temperature: float = Field(default=float(os.getenv("LLM_TEMPERATURE", 0.1)))
    max_tokens: int = Field(default=int(os.getenv("LLM_MAX_TOKENS", 4096)))
    top_p: float = Field(default=float(os.getenv("LLM_TOP_P", 0.95)))


class ChunkingConfig(BaseModel):
    """Text chunking configuration."""

    chunk_size: int = Field(default=int(os.getenv("CHUNK_SIZE", 512)))
    chunk_overlap: int = Field(default=int(os.getenv("CHUNK_OVERLAP", 50)))


class RetrievalConfig(BaseModel):
    """Retrieval configuration."""

    top_k: int = Field(default=int(os.getenv("TOP_K", 5)))
    similarity_threshold: float = Field(
        default=float(os.getenv("SIMILARITY_THRESHOLD", 0.7))
    )


class AppConfig(BaseModel):
    """Application configuration."""

    host: str = Field(default=os.getenv("APP_HOST", "0.0.0.0"))
    port: int = Field(default=int(os.getenv("APP_PORT", 8000)))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    data_dir: Path = Field(default=ROOT_DIR / "data")
    documents_dir: Path = Field(default=ROOT_DIR / "data" / "documents")
    processing_dir: Path = Field(default=ROOT_DIR / "data" / "processing")


class Config(BaseModel):
    """Main configuration class."""

    app: AppConfig = Field(default_factory=AppConfig)
    milvus: MilvusConfig = Field(default_factory=MilvusConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)


# Create global configuration instance
config = Config()

# Ensure required directories exist
os.makedirs(config.app.data_dir, exist_ok=True)
os.makedirs(config.app.documents_dir, exist_ok=True)
os.makedirs(config.app.processing_dir, exist_ok=True)
