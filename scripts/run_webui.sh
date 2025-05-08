#!/bin/bash
# Script to run the Web UI for the unstructured RAG system

set -e  # Exit on error

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEBUI_DIR="$ROOT_DIR/webui"

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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    log "ERROR" "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$WEBUI_DIR/venv" ]; then
    log "INFO" "Creating Python virtual environment for Web UI..."
    cd "$WEBUI_DIR"
    python3 -m venv venv
fi

# Activate virtual environment
source "$WEBUI_DIR/venv/bin/activate"

# Install dependencies
log "INFO" "Installing dependencies..."
cd "$WEBUI_DIR"
pip install --upgrade pip
pip install -r requirements.txt

# Check if the RAG API is running
log "INFO" "Checking if RAG API is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    log "INFO" "RAG API is running."
else
    log "WARNING" "RAG API does not appear to be running. Make sure to start it first with './scripts/setup_run_deploy.sh --run local'"
fi

# Run the Web UI
log "INFO" "Starting Web UI..."
cd "$WEBUI_DIR"
python server.py

# Deactivate virtual environment on exit
deactivate
