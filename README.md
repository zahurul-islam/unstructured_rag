# Unstructured RAG System

A Retrieval-Augmented Generation (RAG) system for processing unstructured data using Milvus vector database and various LLM models. The system provides a user-friendly web interface for document management and natural language querying.

## Features

- Process various unstructured data types (PDF, text, HTML, Word, etc.)
- Vector storage using Milvus database
- Text generation with multiple LLM options (local models or API-based)
- Flexible chunking strategies for optimal document processing
- RESTful API with FastAPI
- User-friendly web interface
- Automatic source attribution in responses
- Natural language responses with comprehensive information
- Docker support

## Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Git

### Quick Start with Helper Script

The project includes a comprehensive setup, run, and deploy script that simplifies the process:

```bash
# Show script help
./scripts/setup_run_deploy.sh --help

# Set up the environment
./scripts/setup_run_deploy.sh --setup

# Run locally (Python + Docker for Milvus)
./scripts/setup_run_deploy.sh --run local

# Run with Docker (full containerization)
./scripts/setup_run_deploy.sh --run docker

# Deploy to production
./scripts/setup_run_deploy.sh --deploy

# Clean the environment
./scripts/setup_run_deploy.sh --clean
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/zahurul-islam/unstructured_rag.git
cd unstructured_rag
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and update it with your settings:
```bash
cp .env.example .env
# Edit .env file with your API keys and settings
```

5. Start Milvus with Docker Compose:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

6. Run the setup script:
```bash
python scripts/setup_milvus.py
```

### Running the API

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

## Usage

### Ingesting Documents

```bash
curl -X POST "http://localhost:8000/documents/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

### Querying

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What information does the document contain about X?"}'
```

## API Endpoints

- `POST /documents/ingest`: Upload and process documents
- `GET /documents`: List all ingested documents
- `POST /query`: Perform RAG query
- `GET /health`: Check system health

## Web Interface

The system includes a user-friendly web interface that allows you to:

- Upload and manage documents through a simple drag-and-drop interface
- View all uploaded documents with metadata
- Delete documents when no longer needed
- Ask natural language questions about your documents
- View comprehensive answers with source attribution
- Navigate between different sections of the application

### Running the Web UI

```bash
# Start the Web UI server
cd webui
python server.py

# Access the Web UI in your browser
# Default URL: http://localhost:8083
```

## Architecture

The system follows a modular architecture:

1. **Data Ingestion**: Processes various file types and extracts text
2. **Processing**: Cleans text, chunks content, and generates embeddings
3. **Retrieval**: Searches for relevant chunks using vector similarity
4. **Generation**: Creates natural language responses based on retrieved information
5. **Web Interface**: Provides a user-friendly interface for document management and querying

### System Components

- **FastAPI Backend**: Handles document processing, vector storage, and query processing
- **Milvus Vector Database**: Stores document embeddings for efficient similarity search
- **LLM Integration**: Supports both local models and API-based models for text generation
- **Flask Web Server**: Serves the web interface and communicates with the backend API
- **Document Processors**: Handle various document formats (PDF, text, HTML, etc.)

## Utility Scripts

The project includes several utility scripts to help with setup, development, and evaluation:

### Setup and Deployment

- **setup_run_deploy.sh**: All-in-one script for setting up, running, and deploying the system
- **setup_milvus.py**: Initialize and configure the Milvus vector database
- **init.py**: Create necessary directories and initialize the project

### Development and Testing

- **benchmark.py**: Performance testing tool for measuring ingestion and query speeds
  ```bash
  # Example: Benchmark document ingestion
  python scripts/benchmark.py --mode ingestion --files data/sample.pdf

  # Example: Benchmark query performance
  python scripts/benchmark.py --mode retrieval --queries "What is RAG?"
  ```

## Examples

The `examples` directory contains Jupyter notebooks demonstrating how to use the system:

- **basic_rag.ipynb**: Basic usage of the RAG system
- **advanced_rag.ipynb**: Advanced features and customization

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black .
isort .
flake8
```

## License

MIT

## Contributors

- Zahurul Islam
