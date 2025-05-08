#!/usr/bin/env python
"""
Benchmark script for comparing CPU vs GPU performance in the RAG system.
"""

import os
import sys
import time
import argparse
import logging
from typing import List, Dict, Any
import torch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import config
from rag.processing.embedder import Embedder
from rag.generation.llm import LLM


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join("logs", "benchmark_gpu.log"))
        ]
    )
    return logging.getLogger(__name__)


def benchmark_embeddings(texts: List[str], use_gpu: bool, batch_size: int, logger):
    """Benchmark embedding generation."""
    logger.info(f"Benchmarking embedding generation with {'GPU' if use_gpu else 'CPU'}")
    
    # Create embedder with GPU or CPU
    embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Force CPU if requested
    if not use_gpu:
        if hasattr(embedder.model, 'cpu'):
            embedder.model.cpu()
        device = "cpu"
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    logger.info(f"Embedder running on: {device}")
    
    # Warm-up
    logger.info("Warming up...")
    embedder.embed_text("Warm-up text to ensure model is loaded")
    
    # Run benchmark
    total_tokens = sum(len(text.split()) for text in texts)
    logger.info(f"Benchmarking {len(texts)} texts with {total_tokens} total tokens")
    
    # Single text benchmark
    start_time = time.time()
    for text in texts[:min(10, len(texts))]:
        embedder.embed_text(text)
    single_elapsed = time.time() - start_time
    single_texts_per_sec = min(10, len(texts)) / single_elapsed
    
    # Batch processing benchmark
    start_time = time.time()
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embedder.embed_texts(batch)
    batch_elapsed = time.time() - start_time
    batch_texts_per_sec = len(texts) / batch_elapsed
    
    # Log results
    logger.info(f"Single text processing: {single_elapsed:.2f}s for {min(10, len(texts))} texts ({single_texts_per_sec:.2f} texts/sec)")
    logger.info(f"Batch processing: {batch_elapsed:.2f}s for {len(texts)} texts ({batch_texts_per_sec:.2f} texts/sec)")
    
    return {
        "device": device,
        "single_elapsed": single_elapsed,
        "single_texts_per_sec": single_texts_per_sec,
        "batch_elapsed": batch_elapsed,
        "batch_texts_per_sec": batch_texts_per_sec,
        "total_tokens": total_tokens,
    }


def benchmark_llm(prompts: List[str], use_gpu: bool, logger):
    """Benchmark LLM inference."""
    logger.info(f"Benchmarking LLM inference with {'GPU' if use_gpu else 'CPU'}")
    
    # Create LLM with GPU or CPU
    llm = LLM(
        model_name="deepseek/deepseek-r1-zero:free",
        use_gpu=use_gpu,
    )
    
    # Get device info
    if hasattr(llm.model, 'device'):
        device = str(llm.model.device)
    elif hasattr(llm.model, 'hf_device_map'):
        device = str(llm.model.hf_device_map)
    else:
        device = "unknown"
    
    logger.info(f"LLM running on: {device}")
    
    # Warm-up
    logger.info("Warming up...")
    llm.generate("Hello, world!")
    
    # Run benchmark
    total_tokens = sum(len(prompt.split()) for prompt in prompts)
    logger.info(f"Benchmarking {len(prompts)} prompts with {total_tokens} total tokens")
    
    # Inference benchmark
    timings = []
    token_counts = []
    
    for prompt in prompts:
        # Measure generation time
        start_time = time.time()
        response = llm.generate(prompt, max_tokens=100)
        elapsed = time.time() - start_time
        
        # Count output tokens
        output_tokens = len(response.split())
        input_tokens = len(prompt.split())
        token_counts.append((input_tokens, output_tokens))
        
        timings.append(elapsed)
    
    # Calculate metrics
    avg_time = sum(timings) / len(timings)
    total_output_tokens = sum(out for _, out in token_counts)
    tokens_per_sec = total_output_tokens / sum(timings)
    
    # Log results
    logger.info(f"Average generation time: {avg_time:.2f}s per prompt")
    logger.info(f"Throughput: {tokens_per_sec:.2f} output tokens/sec")
    
    return {
        "device": device,
        "avg_time": avg_time,
        "timings": timings,
        "tokens_per_sec": tokens_per_sec,
        "total_input_tokens": total_tokens,
        "total_output_tokens": total_output_tokens,
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Benchmark GPU vs CPU performance")
    parser.add_argument("--cpu-only", action="store_true", help="Force CPU usage")
    parser.add_argument("--embedding-only", action="store_true", help="Only benchmark embeddings")
    parser.add_argument("--llm-only", action="store_true", help="Only benchmark LLM")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for embedding")
    
    args = parser.parse_args()
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Set up logging
    logger = setup_logging()
    
    # Check for GPU
    if torch.cuda.is_available() and not args.cpu_only:
        logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
        use_gpu = True
    else:
        if args.cpu_only:
            logger.info("Forcing CPU usage")
        else:
            logger.info("No GPU detected, using CPU")
        use_gpu = False
    
    # Generate test data
    if not args.llm_only:
        logger.info("Preparing embedding benchmark data...")
        
        # Create sample texts of varying lengths
        texts = []
        # Short texts (50-100 tokens)
        for i in range(100):
            tokens = " ".join([f"token{j}" for j in range(50 + i % 50)])
            texts.append(f"Short text {i}: {tokens}")
        
        # Medium texts (200-300 tokens)
        for i in range(50):
            tokens = " ".join([f"token{j}" for j in range(200 + i % 100)])
            texts.append(f"Medium text {i}: {tokens}")
        
        # Long texts (500-600 tokens)
        for i in range(20):
            tokens = " ".join([f"token{j}" for j in range(500 + i % 100)])
            texts.append(f"Long text {i}: {tokens}")
        
        # Run embedding benchmark
        embedding_results = benchmark_embeddings(texts, use_gpu, args.batch_size, logger)
    
    if not args.embedding_only:
        logger.info("Preparing LLM benchmark data...")
        
        # Create sample prompts of varying complexity
        prompts = [
            "What is the capital of France?",
            "Explain the process of photosynthesis.",
            "Write a short summary of the main themes in Shakespeare's Hamlet.",
            "Describe the differences between supervised and unsupervised learning in machine learning.",
            "What are the key features of the Python programming language? List at least five features.",
        ]
        
        # Run LLM benchmark
        llm_results = benchmark_llm(prompts, use_gpu, logger)
    
    # Print summary
    logger.info("=" * 50)
    logger.info("BENCHMARK SUMMARY")
    logger.info("=" * 50)
    
    if not args.llm_only:
        logger.info(f"Embedding Performance ({embedding_results['device']}):")
        logger.info(f"  - Single processing: {embedding_results['single_texts_per_sec']:.2f} texts/sec")
        logger.info(f"  - Batch processing: {embedding_results['batch_texts_per_sec']:.2f} texts/sec")
    
    if not args.embedding_only:
        logger.info(f"LLM Performance ({llm_results['device']}):")
        logger.info(f"  - Average generation time: {llm_results['avg_time']:.2f}s per prompt")
        logger.info(f"  - Throughput: {llm_results['tokens_per_sec']:.2f} tokens/sec")


if __name__ == "__main__":
    main()
