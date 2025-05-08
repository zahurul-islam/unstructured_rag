#!/bin/bash
# Unstructured RAG System: Setup, Run, and Deploy Script
# This script provides options to set up, run, and deploy the RAG system.

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

# Function to display help message
show_help() {
    echo -e "${BLUE}Unstructured RAG System - Setup, Run, and Deploy Script${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -s, --setup                Set up the environment (Python venv, dependencies)"
    echo "  -r, --run [local|docker]   Run the system (locally or with docker)"
    echo "  -d, --deploy               Deploy the system"
    echo "  -c, --clean                Clean the environment"
    echo ""
    echo "Examples:"
    echo "  $0 --setup                 # Set up the environment"
    echo "  $0 --run local             # Run locally"
    echo "  $0 --run docker            # Run with Docker"
    echo "  $0 --deploy                # Deploy to production"
    echo "  $0 --clean                 # Clean the environment"
    echo ""
}

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

# Function to set up the environment
setup_environment() {
    log "INFO" "Setting up the environment..."
    
    # Create necessary directories
    mkdir -p "$ROOT_DIR/data/documents" "$ROOT_DIR/data/processing" "$ROOT_DIR/logs"
    
    # Check if Python is installed
    if ! command_exists python3; then
        log "ERROR" "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    # Create Python virtual environment if it doesn't exist
    if [ ! -d "$ROOT_DIR/venv" ]; then
        log "INFO" "Creating Python virtual environment..."
        python3 -m venv "$ROOT_DIR/venv"
    fi
    
    # Activate virtual environment
    source "$ROOT_DIR/venv/bin/activate"
    
    # Install dependencies
    log "INFO" "Installing dependencies..."
    pip install --upgrade pip
    pip install -r "$ROOT_DIR/requirements.txt"
    
    # Create .env file if it doesn't exist
    if [ ! -f "$ROOT_DIR/.env" ]; then
        log "INFO" "Creating .env file..."
        cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
        log "WARNING" "Please update the .env file with your API keys and configuration."
    fi
    
    log "INFO" "Environment setup completed successfully."
}

# Function to ensure Milvus is running properly
ensure_milvus_running() {
    log "INFO" "Checking Milvus..."
    
    # Check if Milvus containers are running
    MILVUS_RUNNING=$(docker ps | grep milvus-standalone | wc -l)
    ETCD_RUNNING=$(docker ps | grep milvus-etcd | wc -l)
    MINIO_RUNNING=$(docker ps | grep milvus-minio | wc -l)
    
    if [ "$MILVUS_RUNNING" -eq 0 ] || [ "$ETCD_RUNNING" -eq 0 ] || [ "$MINIO_RUNNING" -eq 0 ]; then
        log "INFO" "Starting Milvus with Docker Compose..."
        
        # Stop any existing containers first
        docker-compose -f "$ROOT_DIR/docker/docker-compose.yml" down 2>/dev/null || true
        
        # Start Milvus and its dependencies
        docker-compose -f "$ROOT_DIR/docker/docker-compose.yml" up -d milvus etcd minio createbuckets
        
        # Wait for services to be ready
        log "INFO" "Waiting for Milvus to be ready..."
        sleep 15
    else
        log "INFO" "Milvus is already running."
    fi
    
    # Verify Milvus is responsive
    MAX_RETRIES=3
    RETRY_COUNT=0
    MILVUS_OK=false
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$MILVUS_OK" = false ]; do
        if docker exec milvus-standalone curl -s http://localhost:9091/api/v1/health >/dev/null 2>&1; then
            MILVUS_OK=true
            log "INFO" "Milvus is healthy."
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                log "WARNING" "Milvus is not ready yet. Waiting 10 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
                sleep 10
            else
                log "WARNING" "Milvus might not be fully healthy, but we'll try to proceed anyway."
            fi
        fi
    done
}

# Function to run the system locally
run_local() {
    log "INFO" "Running the system locally..."
    
    # Activate virtual environment
    source "$ROOT_DIR/venv/bin/activate"
    
    # Check if .env file exists
    if [ ! -f "$ROOT_DIR/.env" ]; then
        log "ERROR" ".env file not found. Please run setup first."
        exit 1
    fi
    
    # Start Milvus if not running
    ensure_milvus_running
    
    # Setup Milvus collection
    log "INFO" "Setting up Milvus collection..."
    python3 "$ROOT_DIR/scripts/setup_milvus.py" || {
        log "WARNING" "Milvus setup encountered issues but we'll try to continue."
    }
    
    # Start the API
    log "INFO" "Starting the API..."
    cd "$ROOT_DIR"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to run the system with Docker
run_docker() {
    log "INFO" "Running the system with Docker..."
    
    # Check if .env file exists
    if [ ! -f "$ROOT_DIR/.env" ]; then
        log "ERROR" ".env file not found. Please run setup first."
        exit 1
    fi
    
    # Start the system with Docker Compose
    log "INFO" "Starting the system with Docker Compose..."
    docker-compose -f "$ROOT_DIR/docker/docker-compose.yml" up -d
    
    # Wait for startup
    sleep 10
    
    # Check if the services are running
    MILVUS_RUNNING=$(docker ps | grep milvus-standalone | wc -l)
    API_RUNNING=$(docker ps | grep rag-api | wc -l)
    
    if [ "$MILVUS_RUNNING" -eq 0 ] || [ "$API_RUNNING" -eq 0 ]; then
        log "ERROR" "Some services failed to start. Please check the logs:"
        log "INFO" "Docker logs: docker-compose -f $ROOT_DIR/docker/docker-compose.yml logs"
        exit 1
    fi
    
    log "INFO" "System started successfully. API is available at http://localhost:8000"
    log "INFO" "API documentation is available at http://localhost:8000/docs"
}

# Function to stop the system
stop_system() {
    log "INFO" "Stopping the system..."
    
    # Stop Docker containers
    if command_exists docker-compose; then
        log "INFO" "Stopping Docker containers..."
        docker-compose -f "$ROOT_DIR/docker/docker-compose.yml" down
    fi
    
    log "INFO" "System stopped successfully."
}

# Function to clean the environment
clean_environment() {
    log "WARNING" "Cleaning the environment..."
    
    # Confirm action
    read -p "This will delete all data and volumes. Are you sure? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "INFO" "Cleaning aborted."
        return
    fi
    
    # Stop the system
    stop_system
    
    # Remove Docker volumes
    if command_exists docker; then
        log "INFO" "Removing Docker volumes..."
        docker volume rm $(docker volume ls -q -f name=docker_*) 2>/dev/null || true
    fi
    
    # Remove virtual environment
    if [ -d "$ROOT_DIR/venv" ]; then
        log "INFO" "Removing virtual environment..."
        rm -rf "$ROOT_DIR/venv"
    fi
    
    # Remove data directories
    log "INFO" "Removing data directories..."
    rm -rf "$ROOT_DIR/data/documents/*" "$ROOT_DIR/data/processing/*" "$ROOT_DIR/logs/*"
    
    log "INFO" "Environment cleaned successfully."
}

# Function to deploy the system
deploy_system() {
    log "INFO" "Deploying the system..."
    
    # Check if Docker is installed
    if ! command_exists docker || ! command_exists docker-compose; then
        log "ERROR" "Docker and/or Docker Compose not found. Please install them first."
        exit 1
    fi
    
    # Build Docker image
    log "INFO" "Building Docker image..."
    docker-compose -f "$ROOT_DIR/docker/docker-compose.yml" build
    
    # Check deployment target
    read -p "Deploy to (local/server): " deploy_target
    
    case $deploy_target in
        local)
            log "INFO" "Deploying locally..."
            run_docker
            ;;
        server)
            log "INFO" "Deploying to server..."
            # Check if SSH key is available
            read -p "Enter server address (user@hostname): " server_address
            
            # Check if we can connect to the server
            if ! ssh -q -o BatchMode=yes -o ConnectTimeout=5 "$server_address" exit; then
                log "ERROR" "Cannot connect to server. Please check your SSH key and server address."
                exit 1
            fi
            
            # Copy files to server
            log "INFO" "Copying files to server..."
            rsync -avz --exclude 'venv' --exclude '.git' --exclude '__pycache__' --exclude 'data' "$ROOT_DIR/" "$server_address:~/unstructured_rag"
            
            # Run deploy commands on server
            log "INFO" "Running deploy commands on server..."
            ssh "$server_address" "cd ~/unstructured_rag && docker-compose -f docker/docker-compose.yml up -d"
            
            log "INFO" "System deployed successfully to server."
            ;;
        *)
            log "ERROR" "Unknown deployment target: $deploy_target"
            exit 1
            ;;
    esac
}

# Main script logic
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--setup)
            setup_environment
            shift
            ;;
        -r|--run)
            if [ -z "$2" ] || [[ "$2" == -* ]]; then
                log "ERROR" "Missing run mode (local or docker)"
                exit 1
            fi
            
            case "$2" in
                local)
                    run_local
                    ;;
                docker)
                    run_docker
                    ;;
                *)
                    log "ERROR" "Unknown run mode: $2"
                    exit 1
                    ;;
            esac
            shift 2
            ;;
        -d|--deploy)
            deploy_system
            shift
            ;;
        -c|--clean)
            clean_environment
            shift
            ;;
        --stop)
            stop_system
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

exit 0
