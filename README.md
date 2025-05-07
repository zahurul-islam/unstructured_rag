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

### Installation

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
