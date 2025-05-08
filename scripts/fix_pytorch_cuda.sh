#!/bin/bash
# Script to fix PyTorch CUDA installation

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

# Activate virtual environment
log "INFO" "Activating virtual environment..."
source "$ROOT_DIR/venv/bin/activate"

# Uninstall current PyTorch
log "INFO" "Uninstalling current PyTorch version..."
pip uninstall -y torch torchvision torchaudio

# Install PyTorch with CUDA support
log "INFO" "Installing PyTorch with CUDA support..."
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu121

# Verify installation
log "INFO" "Verifying PyTorch CUDA installation..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"Not available\"}'); print(f'GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

if python -c "import torch; import sys; sys.exit(0 if torch.cuda.is_available() else 1)"; then
    log "INFO" "PyTorch CUDA support verified successfully!"
    
    # Install other GPU dependencies
    log "INFO" "Installing additional GPU dependencies..."
    pip install -U bitsandbytes accelerate
    
    log "INFO" "GPU setup completed. Your RTX 4090 is ready to use with the RAG system!"
else
    log "ERROR" "PyTorch CUDA support installation failed."
    log "INFO" "Please try installing manually with:"
    log "INFO" "source venv/bin/activate && pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu121"
fi
