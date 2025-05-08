#!/usr/bin/env python
"""
Script to verify GPU support for the unstructured RAG system.
"""

import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_torch_gpu():
    """Check PyTorch GPU support."""
    try:
        import torch
        
        logger.info(f"PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            logger.info(f"CUDA available: Yes")
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU device count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            
            # Run a simple test
            logger.info("Running simple tensor operation on GPU...")
            x = torch.rand(1000, 1000).cuda()
            y = torch.rand(1000, 1000).cuda()
            
            start_time = time.time()
            z = torch.matmul(x, y)
            gpu_time = time.time() - start_time
            
            # Run the same operation on CPU
            x_cpu = x.cpu()
            y_cpu = y.cpu()
            
            start_time = time.time()
            z_cpu = torch.matmul(x_cpu, y_cpu)
            cpu_time = time.time() - start_time
            
            logger.info(f"Matrix multiplication time - GPU: {gpu_time:.4f}s, CPU: {cpu_time:.4f}s")
            logger.info(f"GPU speedup: {cpu_time/gpu_time:.2f}x")
            
            return True
        else:
            logger.warning("CUDA is not available in PyTorch")
            return False
    
    except ImportError:
        logger.error("PyTorch is not installed")
        return False
    except Exception as e:
        logger.error(f"Error checking PyTorch GPU support: {str(e)}")
        return False

def check_embedding_model():
    """Check embedding model GPU support."""
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        
        logger.info("Loading embedding model...")
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        start_time = time.time()
        model = SentenceTransformer(model_name, device="cuda" if torch.cuda.is_available() else "cpu")
        load_time = time.time() - start_time
        
        device = next(model.parameters()).device
        logger.info(f"Embedding model loaded on: {device} in {load_time:.2f}s")
        
        # Test embedding generation
        sentences = [
            "This is a test sentence for embedding.",
            "Another sentence to embed for testing GPU acceleration.",
            "Let's see how fast the GPU can process these embeddings."
        ] * 100  # Create 300 sentences
        
        logger.info(f"Generating embeddings for {len(sentences)} sentences...")
        
        start_time = time.time()
        embeddings = model.encode(sentences)
        encoding_time = time.time() - start_time
        
        logger.info(f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
        logger.info(f"Embedding generation time: {encoding_time:.2f}s")
        logger.info(f"Sentences per second: {len(sentences)/encoding_time:.2f}")
        
        return True
    
    except ImportError:
        logger.error("Sentence Transformers is not installed")
        return False
    except Exception as e:
        logger.error(f"Error checking embedding model: {str(e)}")
        return False

def check_transformers_gpu():
    """Check Transformers GPU support."""
    try:
        import transformers
        import torch
        
        logger.info(f"Transformers version: {transformers.__version__}")
        
        if not torch.cuda.is_available():
            logger.warning("CUDA is not available, skipping Transformers GPU test")
            return False
        
        # Load a small model to test
        logger.info("Loading a small model to test GPU integration...")
        
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_name = "sshleifer/tiny-gpt2"  # Very small model for testing
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda")
        
        # Check if model is on GPU
        device = next(model.parameters()).device
        logger.info(f"Model loaded on: {device}")
        
        # Test generation
        prompt = "This is a test of GPU acceleration."
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        
        logger.info("Generating text...")
        
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=20)
        generation_time = time.time() - start_time
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"Generated text: {generated_text}")
        logger.info(f"Generation time: {generation_time:.2f}s")
        
        return True
    
    except ImportError:
        logger.error("Transformers is not installed")
        return False
    except Exception as e:
        logger.error(f"Error checking Transformers GPU support: {str(e)}")
        return False

def main():
    """Main function to check GPU support."""
    logger.info("=== GPU Verification for Unstructured RAG System ===")
    
    # Check PyTorch GPU support
    logger.info("\n=== Checking PyTorch GPU Support ===")
    torch_gpu = check_torch_gpu()
    
    # Check embedding model
    logger.info("\n=== Checking Embedding Model GPU Support ===")
    embedding_gpu = check_embedding_model()
    
    # Check Transformers GPU support
    logger.info("\n=== Checking Transformers GPU Support ===")
    transformers_gpu = check_transformers_gpu()
    
    # Summary
    logger.info("\n=== GPU Support Summary ===")
    logger.info(f"PyTorch GPU Support: {'✅ Yes' if torch_gpu else '❌ No'}")
    logger.info(f"Embedding Model GPU Support: {'✅ Yes' if embedding_gpu else '❌ No'}")
    logger.info(f"Transformers GPU Support: {'✅ Yes' if transformers_gpu else '❌ No'}")
    
    if torch_gpu and embedding_gpu and transformers_gpu:
        logger.info("\n✅ All GPU components are working correctly!")
        logger.info("Your RTX 4090 is ready to accelerate the RAG system.")
        return 0
    else:
        logger.warning("\n⚠️ Some GPU components are not working correctly.")
        logger.info("Please run the install_gpu_dependencies.sh script to fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
