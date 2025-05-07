#!/usr/bin/env python
"""
Benchmark script for testing RAG system performance.
"""

import os
import sys
import time
import argparse
import logging
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import config
from rag.data_ingestion.loader import load_document
from rag.processing.chunker import chunk_text
from rag.processing.embedder import get_embedder
from rag.retrieval.milvus_client import get_milvus_client, store_chunks
from rag.retrieval.search import search_documents
from rag.generation.response import generate_response


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join("logs", "benchmark.log"))
        ]
    )
    return logging.getLogger(__name__)


def benchmark_ingestion(file_paths: List[str], logger):
    """Benchmark document ingestion performance."""
    logger.info("Benchmarking document ingestion")
    
    total_start_time = time.time()
    results = []
    
    for file_path in file_paths:
        logger.info(f"Processing file: {file_path}")
        
        # Measure loading time
        load_start_time = time.time()
        text, metadata = load_document(file_path)
        load_time = time.time() - load_start_time
        
        # Measure chunking time
        chunk_start_time = time.time()
        chunks = chunk_text(text)
        chunk_time = time.time() - chunk_start_time
        
        # Measure embedding time
        embed_start_time = time.time()
        embedder = get_embedder()
        embedder.embed_chunks(chunks)
        embed_time = time.time() - embed_start_time
        
        # Measure storage time
        store_start_time = time.time()
        doc_id = os.path.basename(file_path)
        doc_name = metadata.get("file_name", doc_id)
        store_chunks(chunks, doc_id, doc_name, embedder)
        store_time = time.time() - store_start_time
        
        # Calculate total time
        total_time = load_time + chunk_time + embed_time + store_time
        
        # Record results
        result = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "text_length": len(text),
            "chunk_count": len(chunks),
            "load_time": load_time,
            "chunk_time": chunk_time,
            "embed_time": embed_time,
            "store_time": store_time,
            "total_time": total_time,
        }
        results.append(result)
        
        logger.info(f"Processed {file_path} in {total_time:.2f}s (Load: {load_time:.2f}s, Chunk: {chunk_time:.2f}s, Embed: {embed_time:.2f}s, Store: {store_time:.2f}s)")
    
    total_time = time.time() - total_start_time
    logger.info(f"Total ingestion time: {total_time:.2f}s for {len(file_paths)} files")
    
    return results


def benchmark_retrieval(queries: List[str], logger):
    """Benchmark retrieval performance."""
    logger.info("Benchmarking retrieval performance")
    
    results = []
    
    for query in queries:
        logger.info(f"Processing query: {query}")
        
        # Measure search time
        search_start_time = time.time()
        search_results = search_documents(query)
        search_time = time.time() - search_start_time
        
        # Measure generation time
        generate_start_time = time.time()
        response = generate_response(query, search_results)
        generate_time = time.time() - generate_start_time
        
        # Calculate total time
        total_time = search_time + generate_time
        
        # Record results
        result = {
            "query": query,
            "result_count": len(search_results),
            "search_time": search_time,
            "generate_time": generate_time,
            "total_time": total_time,
        }
        results.append(result)
        
        logger.info(f"Processed query in {total_time:.2f}s (Search: {search_time:.2f}s, Generate: {generate_time:.2f}s)")
        logger.info(f"Response: {response[:100]}...")
    
    return results


def main():
    """Main function for benchmarking."""
    parser = argparse.ArgumentParser(description="Benchmark RAG system performance")
    parser.add_argument("--files", nargs="+", help="Paths to files for ingestion benchmarking")
    parser.add_argument("--queries", nargs="+", help="Queries for retrieval benchmarking")
    parser.add_argument("--mode", choices=["ingestion", "retrieval", "both"], default="both", help="Benchmark mode")
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Set up logging
    logger = setup_logging()
    
    # Run benchmarks
    if args.mode in ["ingestion", "both"] and args.files:
        ingestion_results = benchmark_ingestion(args.files, logger)
    
    if args.mode in ["retrieval", "both"] and args.queries:
        retrieval_results = benchmark_retrieval(args.queries, logger)
    
    logger.info("Benchmark completed")


if __name__ == "__main__":
    main()
