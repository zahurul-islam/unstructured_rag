#!/usr/bin/env python3
"""
Simple script to test if CUDA is working with PyTorch.
"""

try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        print("✅ CUDA is working!")
    else:
        print("❌ CUDA is not available")
except Exception as e:
    print(f"Error: {e}")
