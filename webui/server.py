"""
Simple Flask server to serve the Web UI for the Unstructured RAG system.
This server proxies requests to the RAG API for easier CORS handling.
"""

import os
import logging
import sys
from urllib.parse import urljoin
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
RAG_API_URL = os.environ.get('RAG_API_URL', 'http://localhost:8001')
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8083))

# Debug: Print current directory and template folder
current_dir = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Current directory: {current_dir}")
logger.info(f"Template folder: {os.path.join(current_dir, 'templates')}")
logger.info(f"Templates exist: {os.path.exists(os.path.join(current_dir, 'templates'))}")
logger.info(f"Index.html exists: {os.path.exists(os.path.join(current_dir, 'templates', 'index.html'))}")

# Create Flask app
app = Flask(__name__,
           template_folder=os.path.join(current_dir, 'templates'),
           static_folder=os.path.join(current_dir, 'static'))
CORS(app)

# Routes
@app.route('/')
def index():
    """Render the main page."""
    try:
        logger.info("Rendering index.html template")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return f"Error rendering index.html: {str(e)}", 500

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

# Proxy routes to the RAG API
@app.route('/documents', methods=['GET'])
def get_documents():
    """Proxy to RAG API: Get documents."""
    try:
        response = requests.get(urljoin(RAG_API_URL, '/documents'))
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({"error": "Failed to connect to RAG API"}), 500

@app.route('/documents/<document_id>', methods=['GET', 'DELETE'])
def document_operations(document_id):
    """Proxy to RAG API: Get or delete document."""
    try:
        if request.method == 'GET':
            response = requests.get(urljoin(RAG_API_URL, f'/documents/{document_id}'))
        elif request.method == 'DELETE':
            response = requests.delete(urljoin(RAG_API_URL, f'/documents/{document_id}'))

        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error with document operation: {str(e)}")
        return jsonify({"error": "Failed to connect to RAG API"}), 500

@app.route('/documents/ingest', methods=['POST'])
def ingest_document():
    """Proxy to RAG API: Ingest document."""
    try:
        # Get the file from request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Forward the file to the RAG API
        files = {
            'files': (file.filename, file.read(), file.content_type)
        }

        response = requests.post(
            urljoin(RAG_API_URL, '/documents/ingest'),
            files=files
        )

        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        return jsonify({"error": f"Failed to upload: {str(e)}"}), 500

@app.route('/documents/ingest-multi', methods=['POST'])
def ingest_multiple_documents():
    """Proxy to RAG API: Ingest multiple documents."""
    try:
        # Get files from request
        if 'files' not in request.files:
            return jsonify({"error": "No files part"}), 400

        files_list = request.files.getlist('files')

        if len(files_list) == 0:
            return jsonify({"error": "No files selected"}), 400

        # Process each file
        results = []

        for file in files_list:
            if file.filename == '':
                continue

            # Forward the file to the RAG API
            files = {
                'files': (file.filename, file.read(), file.content_type)
            }

            try:
                response = requests.post(
                    urljoin(RAG_API_URL, '/documents/ingest'),
                    files=files
                )

                if response.ok:
                    data = response.json()
                    results.append({
                        "filename": file.filename,
                        "status": "success",
                        "response": data
                    })
                else:
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "error": f"API returned status {response.status_code}"
                    })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })

        return jsonify({"results": results}), 200
    except Exception as e:
        logger.error(f"Error ingesting multiple documents: {str(e)}")
        return jsonify({"error": f"Failed to upload files: {str(e)}"}), 500

@app.route('/documents/ingest-directory', methods=['POST'])
def ingest_directory():
    """Proxy to RAG API: Ingest all files in a directory."""
    try:
        # Endpoint expects to receive multiple files from a directory
        if 'files' not in request.files:
            return jsonify({"error": "No files part"}), 400

        files_list = request.files.getlist('files')

        if len(files_list) == 0:
            return jsonify({"error": "No files selected"}), 400

        # Process each file
        results = []

        for file in files_list:
            if file.filename == '':
                continue

            # Forward the file to the RAG API
            files = {
                'files': (file.filename, file.read(), file.content_type)
            }

            try:
                response = requests.post(
                    urljoin(RAG_API_URL, '/documents/ingest'),
                    files=files
                )

                if response.ok:
                    data = response.json()
                    results.append({
                        "filename": file.filename,
                        "status": "success",
                        "response": data
                    })
                else:
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "error": f"API returned status {response.status_code}"
                    })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })

        return jsonify({"results": results}), 200
    except Exception as e:
        logger.error(f"Error ingesting directory: {str(e)}")
        return jsonify({"error": f"Failed to upload directory: {str(e)}"}), 500

@app.route('/query', methods=['POST'])
def query():
    """Proxy to RAG API: Query documents."""
    try:
        # Get the query from request
        data = request.json
        logger.info(f"Received query request: {data}")

        if not data or 'query' not in data:
            logger.error("No query provided in request")
            return jsonify({"error": "No query provided"}), 400

        # Forward the query to the RAG API
        logger.info(f"Forwarding query to RAG API: {urljoin(RAG_API_URL, '/query')}")
        response = requests.post(
            urljoin(RAG_API_URL, '/query'),
            json=data
        )

        logger.info(f"Received response from RAG API: {response.status_code}")

        # Log a sample of the response (not the full content to avoid excessive logging)
        response_json = response.json()
        logger.info(f"Response contains answer: {'answer' in response_json}")

        return jsonify(response_json), response.status_code
    except Exception as e:
        logger.error(f"Error querying: {str(e)}")
        return jsonify({
            "error": "Failed to connect to RAG API",
            "details": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Proxy to RAG API: Health check."""
    try:
        response = requests.get(urljoin(RAG_API_URL, '/health'))
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error checking health: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "version": "unknown",
            "details": {
                "api_connection": {
                    "status": "unhealthy",
                    "message": f"Failed to connect to RAG API: {str(e)}"
                }
            }
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info(f"Starting Web UI server on {HOST}:{PORT}")
    logger.info(f"Connecting to RAG API at {RAG_API_URL}")
    app.run(host=HOST, port=PORT, debug=True)
