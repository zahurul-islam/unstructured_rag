#!/bin/bash
# Setup proper GPU-enabled environment for the RAG system

set -e  # Exit on error

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Clean up existing environments if they exist
log "INFO" "Cleaning up existing environments..."
rm -rf venv gpu_env 2>/dev/null || true

# Create a fresh virtual environment
log "INFO" "Creating a fresh Python virtual environment..."
python3 -m venv gpu_env

# Activate the environment
log "INFO" "Activating environment..."
. gpu_env/bin/activate

# Install Python dependencies with GPU support
log "INFO" "Installing PyTorch with CUDA support (this may take a while)..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
log "INFO" "Installing other dependencies..."
pip install -r requirements.txt

# Test GPU support
log "INFO" "Testing GPU support..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"Not available\"}'); print(f'GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# Create symlink so the main scripts can find the new environment
log "INFO" "Creating symlink to the new environment..."
ln -sf gpu_env venv

log "INFO" "Environment setup completed. Use the following to run the system:"
log "INFO" "./scripts/setup_run_deploy.sh --run local"
