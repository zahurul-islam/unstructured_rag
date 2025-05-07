"""
Text chunking module for splitting documents into manageable pieces.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union

from app.config import config

# Configure logging
logger = logging.getLogger(__name__)


class Chunk:
    """
    Represents a document chunk with text content and metadata.
    """
    
    def __init__(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk_index: int,
    ):
        """
        Initialize a chunk.
        
        Args:
            text: Chunk text content
            metadata: Chunk metadata
            chunk_index: Index of the chunk in the document
        """
        self.text = text
        self.metadata = metadata.copy()  # Make a copy to avoid modifying original
        self.metadata["chunk_index"] = chunk_index
        self.embedding = None
    
    def __str__(self) -> str:
        return f"Chunk(index={self.metadata.get('chunk_index')}, len={len(self.text)})"
    
    def __repr__(self) -> str:
        return self.__str__()


def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    strategy: str = "fixed_size",
) -> List[Chunk]:
    """
    Split text into chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        metadata: Metadata to add to each chunk
        strategy: Chunking strategy: "fixed_size", "paragraph", "sentence", or "recursive"
        
    Returns:
        List of Chunk objects
    """
    # Use configuration if not specified
    chunk_size = chunk_size or config.chunking.chunk_size
    chunk_overlap = chunk_overlap or config.chunking.chunk_overlap
    metadata = metadata or {}
    
    # Choose chunking strategy
    if strategy == "fixed_size":
        return chunk_text_fixed_size(text, chunk_size, chunk_overlap, metadata)
    elif strategy == "paragraph":
        return chunk_text_by_paragraph(text, chunk_size, chunk_overlap, metadata)
    elif strategy == "sentence":
        return chunk_text_by_sentence(text, chunk_size, chunk_overlap, metadata)
    elif strategy == "recursive":
        return chunk_text_recursive(text, chunk_size, chunk_overlap, metadata)
    else:
        logger.warning(f"Unknown chunking strategy: {strategy}. Using fixed_size.")
        return chunk_text_fixed_size(text, chunk_size, chunk_overlap, metadata)


def chunk_text_fixed_size(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    metadata: Dict[str, Any],
) -> List[Chunk]:
    """
    Split text into fixed-size chunks with overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        metadata: Metadata to add to each chunk
        
    Returns:
        List of Chunk objects
    """
    # Clean and normalize text
    text = text.strip()
    
    if not text:
        return []
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        # Get chunk text
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        # Create chunk
        chunk = Chunk(
            text=chunk_text,
            metadata=metadata,
            chunk_index=chunk_index,
        )
        chunks.append(chunk)
        
        # Move to next chunk
        start += (chunk_size - chunk_overlap)
        chunk_index += 1
    
    logger.info(f"Split text into {len(chunks)} fixed-size chunks")
    return chunks


def chunk_text_by_paragraph(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    metadata: Dict[str, Any],
) -> List[Chunk]:
    """
    Split text into chunks by paragraph, then combine to meet chunk size.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        metadata: Metadata to add to each chunk
        
    Returns:
        List of Chunk objects
    """
    # Find paragraph breaks
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    
    if not paragraphs:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0
    
    for paragraph in paragraphs:
        paragraph_size = len(paragraph)
        
        # If adding this paragraph would exceed the chunk size, start a new chunk
        if current_size + paragraph_size > chunk_size and current_chunk:
            # Create a chunk
            chunk_text = "\n\n".join(current_chunk)
            chunk = Chunk(
                text=chunk_text,
                metadata=metadata,
                chunk_index=chunk_index,
            )
            chunks.append(chunk)
            
            # Add overlap
            overlap_size = 0
            overlap_chunks = []
            
            # Add paragraphs from the end of the previous chunk for overlap
            for p in reversed(current_chunk):
                if overlap_size + len(p) <= chunk_overlap:
                    overlap_chunks.insert(0, p)
                    overlap_size += len(p)
                else:
                    break
            
            # Start a new chunk with overlap
            current_chunk = overlap_chunks
            current_size = overlap_size
            chunk_index += 1
        
        # Add the paragraph to the current chunk
        current_chunk.append(paragraph)
        current_size += paragraph_size
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunk = Chunk(
            text=chunk_text,
            metadata=metadata,
            chunk_index=chunk_index,
        )
        chunks.append(chunk)
    
    logger.info(f"Split text into {len(chunks)} paragraph-based chunks")
    return chunks


def chunk_text_by_sentence(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    metadata: Dict[str, Any],
) -> List[Chunk]:
    """
    Split text into chunks by sentence, then combine to meet chunk size.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        metadata: Metadata to add to each chunk
        
    Returns:
        List of Chunk objects
    """
    # Find sentence breaks (simple approach)
    sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
    sentences = [s.strip() for s in re.split(sentence_pattern, text) if s.strip()]
    
    if not sentences:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)
        
        # If this sentence alone exceeds chunk size, split it further
        if sentence_size > chunk_size:
            # Add the current chunk if it's not empty
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk = Chunk(
                    text=chunk_text,
                    metadata=metadata,
                    chunk_index=chunk_index,
                )
                chunks.append(chunk)
                chunk_index += 1
                current_chunk = []
                current_size = 0
            
            # Split the long sentence into fixed-size chunks
            for i in range(0, sentence_size, chunk_size - chunk_overlap):
                end = min(i + chunk_size, sentence_size)
                chunk_text = sentence[i:end]
                chunk = Chunk(
                    text=chunk_text,
                    metadata=metadata,
                    chunk_index=chunk_index,
                )
                chunks.append(chunk)
                chunk_index += 1
            
            continue
        
        # If adding this sentence would exceed the chunk size, start a new chunk
        if current_size + sentence_size > chunk_size and current_chunk:
            # Create a chunk
            chunk_text = " ".join(current_chunk)
            chunk = Chunk(
                text=chunk_text,
                metadata=metadata,
                chunk_index=chunk_index,
            )
            chunks.append(chunk)
            
            # Add overlap
            overlap_size = 0
            overlap_sentences = []
            
            # Add sentences from the end of the previous chunk for overlap
            for s in reversed(current_chunk):
                if overlap_size + len(s) <= chunk_overlap:
                    overlap_sentences.insert(0, s)
                    overlap_size += len(s)
                else:
                    break
            
            # Start a new chunk with overlap
            current_chunk = overlap_sentences
            current_size = overlap_size
            chunk_index += 1
        
        # Add the sentence to the current chunk
        current_chunk.append(sentence)
        current_size += sentence_size
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunk = Chunk(
            text=chunk_text,
            metadata=metadata,
            chunk_index=chunk_index,
        )
        chunks.append(chunk)
    
    logger.info(f"Split text into {len(chunks)} sentence-based chunks")
    return chunks


def chunk_text_recursive(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    metadata: Dict[str, Any],
) -> List[Chunk]:
    """
    Split text recursively using different separators.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        metadata: Metadata to add to each chunk
        
    Returns:
        List of Chunk objects
    """
    # Define separators by priority
    separators = [
        "\n\n",  # Double newline (paragraph)
        "\n",    # Single newline
        ". ",    # Period and space (sentence)
        ", ",    # Comma and space (clause)
        " ",     # Space (word)
        ""       # Empty string (character)
    ]
    
    chunks = []
    chunk_index = 0
    
    def _recursive_chunk(text: str, separators: List[str], chunk_index: int) -> List[Chunk]:
        """Recursively split text using separators."""
        # Base case: if text is short enough
        if len(text) <= chunk_size:
            return [Chunk(text=text, metadata=metadata, chunk_index=chunk_index)]
        
        # If we've run out of separators, use fixed-size chunking
        if not separators:
            return chunk_text_fixed_size(text, chunk_size, chunk_overlap, metadata)
        
        # Try to split with the current separator
        separator = separators[0]
        splits = text.split(separator)
        
        # If the split doesn't help (only one piece), move to next separator
        if len(splits) == 1:
            return _recursive_chunk(text, separators[1:], chunk_index)
        
        # Process each split recursively
        results = []
        current_chunks = []
        current_length = 0
        
        for split in splits:
            # Add separator back, except for the empty string separator
            piece = split + separator if separator and split != splits[-1] else split
            
            # If this piece alone is too big, recursively chunk it
            if len(piece) > chunk_size:
                # Emit the current buffer if it exists
                if current_chunks:
                    chunk_text = "".join(current_chunks)
                    results.append(Chunk(
                        text=chunk_text,
                        metadata=metadata,
                        chunk_index=chunk_index,
                    ))
                    chunk_index += 1
                    current_chunks = []
                    current_length = 0
                
                # Recursively chunk the large piece
                sub_chunks = _recursive_chunk(piece, separators[1:], chunk_index)
                results.extend(sub_chunks)
                chunk_index += len(sub_chunks)
                continue
            
            # If adding this piece would exceed the chunk size, emit the buffer
            if current_length + len(piece) > chunk_size and current_chunks:
                chunk_text = "".join(current_chunks)
                results.append(Chunk(
                    text=chunk_text,
                    metadata=metadata,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1
                
                # Handle overlap
                remaining_text = chunk_text
                overlap_text = ""
                
                # Work backwards to find a point close to the overlap size
                current_sep = separator
                for sep in separators:
                    if sep and sep in remaining_text:
                        # Find the last occurrence of the separator within the overlap region
                        overlap_point = remaining_text.rfind(sep, len(remaining_text) - chunk_overlap)
                        if overlap_point != -1 and overlap_point > len(remaining_text) - chunk_overlap * 2:
                            overlap_text = remaining_text[overlap_point + len(sep):]
                            current_sep = sep
                            break
                
                # If no separator was found, just use the last chunk_overlap characters
                if not overlap_text and chunk_overlap > 0:
                    overlap_text = remaining_text[-chunk_overlap:]
                
                current_chunks = [overlap_text]
                current_length = len(overlap_text)
            
            # Add the piece to the current buffer
            current_chunks.append(piece)
            current_length += len(piece)
        
        # Emit any remaining pieces
        if current_chunks:
            chunk_text = "".join(current_chunks)
            results.append(Chunk(
                text=chunk_text,
                metadata=metadata,
                chunk_index=chunk_index,
            ))
        
        return results
    
    chunks = _recursive_chunk(text, separators, chunk_index)
    logger.info(f"Split text into {len(chunks)} recursive chunks")
    return chunks
