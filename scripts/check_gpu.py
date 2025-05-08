#!/usr/bin/env python
"""
Simple script to check if CUDA and GPU are available in PyTorch.
"""

import sys

try:
    import torch
    
    print(f"PyTorch version: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"CUDA is available!")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        
        # Perform a simple tensor operation on GPU
        print("\nPerforming a simple tensor operation on GPU...")
        x = torch.rand(1000, 1000).cuda()
        y = torch.rand(1000, 1000).cuda()
        
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        
        start.record()
        z = torch.matmul(x, y)
        end.record()
        
        torch.cuda.synchronize()
        gpu_time = start.elapsed_time(end) / 1000  # Convert to seconds
        
        # Same operation on CPU
        x_cpu = x.cpu()
        y_cpu = y.cpu()
        
        start_cpu = torch.cuda.Event(enable_timing=True)
        end_cpu = torch.cuda.Event(enable_timing=True)
        
        start_cpu.record()
        z_cpu = torch.matmul(x_cpu, y_cpu)
        end_cpu.record()
        
        torch.cuda.synchronize()
        cpu_time = start_cpu.elapsed_time(end_cpu) / 1000  # Convert to seconds
        
        print(f"GPU time: {gpu_time:.4f}s")
        print(f"CPU time: {cpu_time:.4f}s")
        print(f"Speedup: {cpu_time/gpu_time:.2f}x")
        
        print("\n✅ PyTorch GPU support is working correctly!")
        sys.exit(0)
    else:
        print("CUDA is not available. PyTorch is using CPU.")
        sys.exit(1)

except ImportError:
    print("PyTorch is not installed.")
    sys.exit(1)

except Exception as e:
    print(f"Error checking GPU: {str(e)}")
    sys.exit(1)
