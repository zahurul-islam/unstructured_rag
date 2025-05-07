# Unstructured RAG System

A Retrieval-Augmented Generation (RAG) system for processing unstructured data using DeepSeek-R1-Zero, Milvus, and LangChain.

## Features

- Process various unstructured data types (PDF, text, HTML, Word, etc.)
- Vector storage using Milvus database
- Text generation with DeepSeek-R1-Zero model
- Flexible chunking strategies
- RESTful API with FastAPI
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

## Architecture

The system follows a modular architecture:

1. **Data Ingestion**: Processes various file types and extracts text
2. **Processing**: Cleans text, chunks content, and generates embeddings
3. **Retrieval**: Searches for relevant chunks using vector similarity
4. **Generation**: Creates responses based on retrieved information

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
