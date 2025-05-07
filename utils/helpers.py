"""
Helper functions for the RAG system.
"""

import os
import hashlib
import json
import time
from typing import Dict, Any, List

from app.config import config


def get_file_hash(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hex digest of the file hash
    """
    hash_obj = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def save_metadata(metadata: Dict[str, Any], file_path: str):
    """
    Save metadata to a JSON file.
    
    Args:
        metadata: Metadata dictionary
        file_path: Path to save the metadata
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save metadata
    with open(file_path, "w") as f:
        json.dump(metadata, f, indent=2)


def load_metadata(file_path: str) -> Dict[str, Any]:
    """
    Load metadata from a JSON file.
    
    Args:
        file_path: Path to the metadata file
        
    Returns:
        Metadata dictionary
    """
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, "r") as f:
        return json.load(f)


def create_progress_tracker():
    """
    Create a progress tracker for long-running tasks.
    
    Returns:
        Dictionary with progress tracking functions
    """
    progress = {
        "total": 0,
        "completed": 0,
        "start_time": time.time(),
        "last_update_time": time.time(),
        "status": "initialized",
        "message": "",
        "errors": [],
    }
    
    def set_total(total: int):
        """Set the total number of items to process."""
        progress["total"] = total
        progress["status"] = "in_progress"
    
    def increment(count: int = 1, message: str = None):
        """Increment the completed count."""
        progress["completed"] += count
        progress["last_update_time"] = time.time()
        if message:
            progress["message"] = message
    
    def add_error(error: str):
        """Add an error message."""
        progress["errors"].append(error)
    
    def complete(message: str = "Task completed"):
        """Mark the task as complete."""
        progress["status"] = "completed"
        progress["message"] = message
        progress["last_update_time"] = time.time()
    
    def fail(message: str):
        """Mark the task as failed."""
        progress["status"] = "failed"
        progress["message"] = message
        progress["last_update_time"] = time.time()
    
    def get_progress() -> Dict[str, Any]:
        """Get the current progress."""
        elapsed = time.time() - progress["start_time"]
        result = {
            **progress,
            "elapsed_seconds": elapsed,
            "percent_complete": (progress["completed"] / progress["total"] * 100) if progress["total"] > 0 else 0,
        }
        return result
    
    return {
        "set_total": set_total,
        "increment": increment,
        "add_error": add_error,
        "complete": complete,
        "fail": fail,
        "get_progress": get_progress,
    }


def format_time(seconds: float) -> str:
    """
    Format time in seconds to a human-readable format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
