#!/bin/bash
# Simple script to wait for PyTorch installation to complete

echo "Waiting for PyTorch installation to complete..."
while ps -p 29209 > /dev/null; do
    echo "Still installing PyTorch with CUDA support..."
    sleep 10
done

echo "Installation process completed. Checking CUDA support..."
cd /home/zahurul/Documents/work/playground/unstructured_rag && . venv/bin/activate && python scripts/check_gpu.py
