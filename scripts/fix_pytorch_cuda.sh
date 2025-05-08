#!/bin/bash
# Script to fix PyTorch CUDA support

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

# Check if virtual environment exists
if [ ! -d "$ROOT_DIR/venv" ]; then
    log "ERROR" "Virtual environment not found at: $ROOT_DIR/venv"
    log "INFO" "Creating a new virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source "$ROOT_DIR/venv/bin/activate"

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    log "ERROR" "NVIDIA GPU not detected. This script requires an NVIDIA GPU."
    exit 1
fi

# Get CUDA version
CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | cut -d. -f1,2 | sed 's/\.//')
log "INFO" "Detected CUDA version from driver: $CUDA_VERSION"

# Select PyTorch installation command based on CUDA version
if [ "$CUDA_VERSION" -ge "120" ]; then
    PYTORCH_INSTALL="pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
    log "INFO" "Using CUDA 12.1 PyTorch packages"
elif [ "$CUDA_VERSION" -ge "118" ]; then
    PYTORCH_INSTALL="pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    log "INFO" "Using CUDA 11.8 PyTorch packages"
elif [ "$CUDA_VERSION" -ge "117" ]; then
    PYTORCH_INSTALL="pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117"
    log "INFO" "Using CUDA 11.7 PyTorch packages"
elif [ "$CUDA_VERSION" -ge "116" ]; then
    PYTORCH_INSTALL="pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu116"
    log "INFO" "Using CUDA 11.6 PyTorch packages"
else
    log "WARNING" "Could not determine a matching PyTorch version for your CUDA version"
    log "INFO" "Using latest CUDA 11.8 PyTorch packages"
    PYTORCH_INSTALL="pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
fi

# Uninstall current PyTorch
log "INFO" "Uninstalling current PyTorch installation..."
pip uninstall -y torch torchvision torchaudio

# Install PyTorch with CUDA support
log "INFO" "Installing PyTorch with CUDA support..."
eval $PYTORCH_INSTALL

# Install other dependencies
log "INFO" "Installing other dependencies..."
pip install -r requirements.txt

# Verify installation
log "INFO" "Verifying PyTorch CUDA support..."
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda); print('GPU device count:', torch.cuda.device_count()); print('Current device:', torch.cuda.current_device()); print('Device name:', torch.cuda.get_device_name(0))"

log "INFO" "PyTorch installation completed."
log "INFO" "You can now run the application with CUDA support."
