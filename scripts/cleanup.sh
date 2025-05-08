#!/bin/bash
# Cleanup script for unnecessary files and directories

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

# Function to remove a directory or file with confirmation
remove_with_confirmation() {
    local path="$1"
    local is_force="$2"
    
    if [ -e "$path" ]; then
        if [ "$is_force" == "force" ] || [ "$FORCE_REMOVE" == "yes" ]; then
            if [ -d "$path" ]; then
                log "INFO" "Removing directory: $path"
                rm -rf "$path"
            else
                log "INFO" "Removing file: $path"
                rm -f "$path"
            fi
        else
            read -p "Do you want to remove $([ -d "$path" ] && echo "directory" || echo "file") '$path'? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if [ -d "$path" ]; then
                    log "INFO" "Removing directory: $path"
                    rm -rf "$path"
                else
                    log "INFO" "Removing file: $path"
                    rm -f "$path"
                fi
            else
                log "INFO" "Skipping: $path"
            fi
        fi
    else
        log "WARNING" "Path does not exist: $path"
    fi
}

# Show help
show_help() {
    echo -e "${BLUE}Unstructured RAG System - Cleanup Script${NC}"
    echo ""
    echo "This script removes unnecessary files and directories from the project."
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help                Show this help message"
    echo "  -y, --yes                 Answer yes to all prompts (force mode)"
    echo "  -v, --venvs               Remove all virtual environments"
    echo "  -c, --cache               Remove all __pycache__ directories"
    echo "  -e, --empty               Remove empty directories"
    echo "  -a, --all                 Remove all unnecessary files and directories"
    echo ""
}

# Parse command line arguments
FORCE_REMOVE="no"
REMOVE_VENVS="no"
REMOVE_CACHE="no"
REMOVE_EMPTY="no"

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -y|--yes)
            FORCE_REMOVE="yes"
            shift
            ;;
        -v|--venvs)
            REMOVE_VENVS="yes"
            shift
            ;;
        -c|--cache)
            REMOVE_CACHE="yes"
            shift
            ;;
        -e|--empty)
            REMOVE_EMPTY="yes"
            shift
            ;;
        -a|--all)
            REMOVE_VENVS="yes"
            REMOVE_CACHE="yes"
            REMOVE_EMPTY="yes"
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main cleanup logic
log "INFO" "Starting cleanup..."

# Remove virtual environments
if [ "$REMOVE_VENVS" == "yes" ]; then
    log "INFO" "Removing virtual environments..."
    
    # Remove gpu_env directory
    remove_with_confirmation "$ROOT_DIR/gpu_env"
    
    # Remove venv file (if it's a file, not a directory)
    if [ -f "$ROOT_DIR/venv" ]; then
        remove_with_confirmation "$ROOT_DIR/venv"
    fi
    
    # Check if rag directory contains a virtual environment
    if [ -d "$ROOT_DIR/rag/bin" ] && [ -d "$ROOT_DIR/rag/lib" ]; then
        log "WARNING" "The rag directory appears to contain a virtual environment"
        log "WARNING" "Please verify before removing, as this might be part of the application structure"
        
        read -p "Do you want to clean up the virtual environment inside the rag directory? This is potentially dangerous! (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            remove_with_confirmation "$ROOT_DIR/rag/bin"
            remove_with_confirmation "$ROOT_DIR/rag/include"
            remove_with_confirmation "$ROOT_DIR/rag/lib"
            remove_with_confirmation "$ROOT_DIR/rag/lib64"
            remove_with_confirmation "$ROOT_DIR/rag/pyvenv.cfg"
            remove_with_confirmation "$ROOT_DIR/rag/share"
        else
            log "INFO" "Skipping cleanup of the rag directory"
        fi
    fi
    
    # Remove webui virtual environments
    remove_with_confirmation "$ROOT_DIR/webui/debug_venv"
    remove_with_confirmation "$ROOT_DIR/webui/venv"
fi

# Remove all __pycache__ directories
if [ "$REMOVE_CACHE" == "yes" ]; then
    log "INFO" "Removing __pycache__ directories..."
    
    # Find all __pycache__ directories
    mapfile -t PYCACHE_DIRS < <(find "$ROOT_DIR" -name "__pycache__" -type d)
    
    if [ ${#PYCACHE_DIRS[@]} -eq 0 ]; then
        log "INFO" "No __pycache__ directories found"
    else
        log "INFO" "Found ${#PYCACHE_DIRS[@]} __pycache__ directories"
        
        if [ "$FORCE_REMOVE" == "yes" ]; then
            log "INFO" "Removing all __pycache__ directories..."
            find "$ROOT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        else
            read -p "Do you want to remove all __pycache__ directories? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log "INFO" "Removing all __pycache__ directories..."
                find "$ROOT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
            else
                log "INFO" "Skipping removal of __pycache__ directories"
            fi
        fi
    fi
fi

# Remove empty directories
if [ "$REMOVE_EMPTY" == "yes" ]; then
    log "INFO" "Handling empty directories..."
    
    # Find all empty directories
    mapfile -t EMPTY_DIRS < <(find "$ROOT_DIR" -type d -empty | grep -v "\.git")
    
    if [ ${#EMPTY_DIRS[@]} -eq 0 ]; then
        log "INFO" "No empty directories found"
    else
        log "INFO" "Found ${#EMPTY_DIRS[@]} empty directories (excluding .git)"
        
        # Create the directories that should exist even if empty
        mkdir -p "$ROOT_DIR/logs"
        mkdir -p "$ROOT_DIR/data/processing"
        
        for dir in "${EMPTY_DIRS[@]}"; do
            # Skip certain directories that should remain
            if [[ "$dir" == "$ROOT_DIR/logs" ]] || [[ "$dir" == "$ROOT_DIR/data/processing" ]]; then
                log "INFO" "Keeping empty directory: $dir"
                continue
            fi
            
            remove_with_confirmation "$dir"
        done
    fi
fi

log "INFO" "Cleanup completed successfully."
