#!/usr/bin/env python
"""
GPU Verification Script for Medical Chatbot Backend
This script verifies that GPU is available and being used correctly
"""

import torch
import sys

def check_gpu():
    """Check if GPU is available and usable"""
    print("=" * 60)
    print("GPU VERIFICATION FOR MEDICAL CHATBOT BACKEND")
    print("=" * 60)
    
    # Check PyTorch CUDA availability
    print(f"\n✓ PyTorch Version: {torch.__version__}")
    print(f"✓ CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"\n✓ GPU DETECTED!")
        print(f"  Device Count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"\n  GPU {i}: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"    - Memory: {props.total_memory / 1e9:.2f} GB")
            print(f"    - Compute Capability: {props.major}.{props.minor}")
        
        # Get current GPU usage
        print(f"\n✓ Current GPU Memory Usage:")
        for i in range(torch.cuda.device_count()):
            allocated = torch.cuda.memory_allocated(i) / 1e9
            reserved = torch.cuda.memory_reserved(i) / 1e9
            print(f"  GPU {i}: {allocated:.2f} GB allocated, {reserved:.2f} GB reserved")
        
        print("\n✅ GPU is ready for inference!")
        return True
    else:
        print("\n❌ GPU NOT FOUND")
        print("\nTo use GPU, ensure:")
        print("  1. NVIDIA GPU driver is installed")
        print("  2. CUDA Toolkit is installed")
        print("  3. PyTorch is installed with CUDA support:")
        print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("\nFalling back to CPU (slower inference)")
        return False

if __name__ == "__main__":
    success = check_gpu()
    sys.exit(0 if success else 1)
