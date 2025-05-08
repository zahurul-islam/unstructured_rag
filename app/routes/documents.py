"""
Document handling endpoints.
"""

import os
import shutil
import uuid
import mimetypes
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import config
from app.services.document_service import process_document

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class DocumentMetadata(BaseModel):
    """Document metadata model."""

    id: str
    filename: str
    content_type: str
    upload_time: datetime
    size_bytes: int
    status: str
    chunk_count: Optional[int] = None


class DocumentResponse(BaseModel):
    """Document response model."""

    documents: List[DocumentMetadata]
    total: int


class DocumentIngestResponse(BaseModel):
    """Document ingestion response model."""

    id: str
    filename: str
    status: str
    message: str


@router.post("/ingest", response_model=List[DocumentIngestResponse])
async def ingest_document(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """
    Upload and process multiple documents.
    """
    responses = []
    
    for file in files:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Extract file extension
        original_filename = file.filename
        if not original_filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Get file extension
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # Check supported file types
        supported_extensions = [
            ".pdf", ".txt", ".html", ".htm", ".docx", 
            ".doc", ".rtf", ".md", ".json", ".csv"
        ]
        
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported types: {', '.join(supported_extensions)}"
            )
        
        # Save file to documents directory
        file_path = os.path.join(config.app.documents_dir, f"{doc_id}{file_extension}")
        
        try:
            # Create documents directory if it doesn't exist
            os.makedirs(config.app.documents_dir, exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            # Close uploaded file
            await file.close()
        
        # Store metadata
        metadata = DocumentMetadata(
            id=doc_id,
            filename=original_filename,
            content_type=file.content_type or "application/octet-stream",
            upload_time=datetime.now(),
            size_bytes=os.path.getsize(file_path),
            status="uploaded"
        )
        
        # Save metadata
        metadata_file = os.path.join(config.app.documents_dir, f"{doc_id}.metadata.json")
        with open(metadata_file, "w") as f:
            f.write(metadata.model_dump_json(indent=2))
        
        # Add document processing to background tasks
        background_tasks.add_task(process_document, doc_id, file_path, file_extension)
        
        # Add response for this file
        responses.append(DocumentIngestResponse(
            id=doc_id,
            filename=original_filename,
            status="processing",
            message="Document uploaded and processing started"
        ))
    
    return responses


@router.get("", response_model=DocumentResponse)
async def list_documents():
    """
    List all ingested documents.
    """
    documents = []
    
    # Scan documents directory for metadata files
    for filename in os.listdir(config.app.documents_dir):
        if filename.endswith(".metadata.json"):
            metadata_path = os.path.join(config.app.documents_dir, filename)
            try:
                with open(metadata_path, "r") as f:
                    # Convert JSON to DocumentMetadata
                    document = DocumentMetadata.model_validate_json(f.read())
                    documents.append(document)
            except Exception as e:
                # Skip invalid metadata files
                continue
    
    # Sort documents by upload time (newest first)
    documents.sort(key=lambda x: x.upload_time, reverse=True)
    
    return DocumentResponse(
        documents=documents,
        total=len(documents)
    )


@router.delete("/{document_id}", response_model=dict)
async def delete_document(document_id: str, background_tasks: BackgroundTasks):
    """
    Delete a document and its associated data.
    """
    # Check if document exists
    metadata_path = os.path.join(config.app.documents_dir, f"{document_id}.metadata.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata to get filename
    try:
        with open(metadata_path, "r") as f:
            document = DocumentMetadata.model_validate_json(f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read document metadata: {str(e)}")
    
    # Delete document file
    file_extensions = [".pdf", ".txt", ".html", ".htm", ".docx", ".doc", ".rtf", ".md", ".json", ".csv"]
    deleted_files = []
    
    for ext in file_extensions:
        file_path = os.path.join(config.app.documents_dir, f"{document_id}{ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_files.append(file_path)
    
    # Delete metadata file
    os.remove(metadata_path)
    deleted_files.append(metadata_path)
    
    # Delete document chunks from Milvus in a background task
    background_tasks.add_task(delete_document_chunks, document_id)
    
    return {
        "message": f"Document '{document.filename}' deleted",
        "deleted_files": deleted_files
    }


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str):
    """
    Get document metadata by ID.
    """
    metadata_path = os.path.join(config.app.documents_dir, f"{document_id}.metadata.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        with open(metadata_path, "r") as f:
            document = DocumentMetadata.model_validate_json(f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read document metadata: {str(e)}")
    
    return document


# Import update_document_status from utils
from app.services.document_utils import update_document_status


def delete_document_chunks(document_id: str):
    """
    Delete document chunks from Milvus.
    
    Args:
        document_id: Document ID
    """
    try:
        # Import services
        from rag.retrieval.milvus_client import get_milvus_client
        
        # Get Milvus client
        milvus_client = get_milvus_client()
        
        # Delete document chunks
        expr = f'document_id == "{document_id}"'
        milvus_client.delete(config.milvus.collection, expr)
        
        print(f"Deleted chunks for document {document_id} from Milvus")
    except Exception as e:
        print(f"Failed to delete document chunks from Milvus: {str(e)}")


@router.post("/ingest-directory", response_model=List[DocumentIngestResponse])
async def ingest_directory(
    background_tasks: BackgroundTasks,
    directory_path: str = Form(...),
    recursive: bool = Form(False),
):
    """
    Process all documents in a directory.
    """
    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=400, detail=f"Directory not found: {directory_path}")
    
    # Supported file extensions
    supported_extensions = [
        ".pdf", ".txt", ".html", ".htm", ".docx", 
        ".doc", ".rtf", ".md", ".json", ".csv"
    ]
    
    # Find all files in the directory
    files_to_process = []
    
    if recursive:
        # Walk through all subdirectories
        for root, _, files in os.walk(directory_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in supported_extensions:
                    files_to_process.append((file_path, filename, file_extension))
    else:
        # Only process files in the top directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in supported_extensions:
                    files_to_process.append((file_path, filename, file_extension))
    
    if not files_to_process:
        raise HTTPException(
            status_code=400, 
            detail=f"No supported files found in the directory. Supported types: {', '.join(supported_extensions)}"
        )
    
    responses = []
    
    # Process each file
    for file_path, filename, file_extension in files_to_process:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Create target path in the documents directory
        target_path = os.path.join(config.app.documents_dir, f"{doc_id}{file_extension}")
        
        try:
            # Create documents directory if it doesn't exist
            os.makedirs(config.app.documents_dir, exist_ok=True)
            
            # Copy file to documents directory
            shutil.copy2(file_path, target_path)
            
            # Get file size
            size_bytes = os.path.getsize(target_path)
            
            # Guess content type
            content_type, _ = mimetypes.guess_type(file_path)
            
            # Store metadata
            metadata = DocumentMetadata(
                id=doc_id,
                filename=filename,
                content_type=content_type or "application/octet-stream",
                upload_time=datetime.now(),
                size_bytes=size_bytes,
                status="uploaded"
            )
            
            # Save metadata
            metadata_file = os.path.join(config.app.documents_dir, f"{doc_id}.metadata.json")
            with open(metadata_file, "w") as f:
                f.write(metadata.model_dump_json(indent=2))
            
            # Add document processing to background tasks
            background_tasks.add_task(process_document, doc_id, target_path, file_extension)
            
            # Add response for this file
            responses.append(DocumentIngestResponse(
                id=doc_id,
                filename=filename,
                status="processing",
                message="Document uploaded and processing started"
            ))
        
        except Exception as e:
            # Log the error but continue processing other files
            logger.error(f"Error processing file {file_path}: {str(e)}")
            responses.append(DocumentIngestResponse(
                id=doc_id,
                filename=filename,
                status="error",
                message=f"Error: {str(e)}"
            ))
    
    return responses
