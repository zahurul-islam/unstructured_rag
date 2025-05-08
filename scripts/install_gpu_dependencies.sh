#!/bin/bash
# Script to install GPU-accelerated dependencies for unstructured RAG system

set -e  # Exit on error

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Function to log messages
log() {
    local level=$1
    local message=$2
    local color=$GREEN
    
    case $level in
        "INFO") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
        *) color=$GREEN ;;
    esac
    
    echo -e "${color}[$level] $message${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for GPU driver
if ! command_exists nvidia-smi; then
    log "ERROR" "NVIDIA drivers not found. Please install NVIDIA drivers first."
    exit 1
fi

# Display GPU information
log "INFO" "Checking GPU..."
GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader)
log "INFO" "NVIDIA GPU detected: $GPU_INFO"

# Get CUDA version from driver
CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | cut -d'.' -f1)
log "INFO" "Detected CUDA compatibility version: $CUDA_VERSION"

# Determine PyTorch CUDA version to install
if [ "$CUDA_VERSION" -ge 12 ]; then
    TORCH_CUDA="cu121"
    log "INFO" "Using CUDA 12.1 for PyTorch"
elif [ "$CUDA_VERSION" -ge 11 ] && [ "$CUDA_VERSION" -lt 12 ]; then
    TORCH_CUDA="cu118"
    log "INFO" "Using CUDA 11.8 for PyTorch"
else
    log "WARNING" "CUDA version $CUDA_VERSION may not be fully supported. Defaulting to CUDA 11.8."
    TORCH_CUDA="cu118"
fi

# Create or activate virtual environment
if [ ! -d "$ROOT_DIR/venv" ]; then
    log "INFO" "Creating Python virtual environment..."
    python3 -m venv "$ROOT_DIR/venv"
fi

log "INFO" "Activating virtual environment..."
source "$ROOT_DIR/venv/bin/activate"

# Install PyTorch with CUDA support
log "INFO" "Installing PyTorch with CUDA support ($TORCH_CUDA)..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$TORCH_CUDA

# Verify PyTorch CUDA installation
log "INFO" "Verifying PyTorch CUDA support..."
PYTORCH_CUDA=$(python3 -c "import torch; print(f'PyTorch version: {torch.__version__}, CUDA available: {torch.cuda.is_available()}, CUDA version: {torch.version.cuda if torch.cuda.is_available() else "N/A"}')")
log "INFO" "$PYTORCH_CUDA"

if python3 -c "import torch; import sys; sys.exit(0 if torch.cuda.is_available() else 1)"; then
    log "INFO" "PyTorch CUDA support verified successfully."
    
    # Install other dependencies
    log "INFO" "Installing other dependencies..."
    pip install -r "$ROOT_DIR/requirements.txt"
    
    # Install additional dependencies for GPU acceleration
    log "INFO" "Installing GPU acceleration dependencies..."
    pip install bitsandbytes==0.42.0 accelerate==0.33.0
    
    log "INFO" "GPU dependencies installed successfully. System is ready to use your RTX 4090!"
else
    log "ERROR" "PyTorch CUDA support installation failed."
    log "INFO" "Troubleshooting tips:"
    log "INFO" "1. Make sure your NVIDIA drivers are up to date"
    log "INFO" "2. Check CUDA toolkit installation"
    log "INFO" "3. Try manually installing with: pip install torch --extra-index-url https://download.pytorch.org/whl/cu121"
    exit 1
fi
