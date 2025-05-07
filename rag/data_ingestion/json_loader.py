"""
JSON document loader.
"""

import os
import json
import logging
from typing import Dict, Tuple, Any

# Configure logging
logger = logging.getLogger(__name__)


def load_json(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a JSON file and convert it to text format.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Tuple containing:
            - Text representation of JSON (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Convert to text representation
        text = json_to_text(data)
        
        # Determine if it's an array or object
        is_array = isinstance(data, list)
        top_level_keys = list(data.keys()) if isinstance(data, dict) else []
        
        # Create JSON-specific metadata
        metadata = {
            "source_type": "json",
            "is_array": is_array,
            "array_length": len(data) if is_array else None,
            "top_level_keys": top_level_keys if not is_array else None
        }
        
        return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading JSON file: {str(e)}")
        
        # Return empty text with error metadata
        return "", {
            "source_type": "json",
            "extraction_error": str(e),
            "extraction_success": False
        }


def json_to_text(data: Any, prefix: str = "", max_depth: int = 5, current_depth: int = 0) -> str:
    """
    Convert JSON data to a structured text representation.
    
    Args:
        data: JSON data (can be dict, list, or primitive)
        prefix: Prefix for the current line
        max_depth: Maximum depth to traverse
        current_depth: Current depth level
        
    Returns:
        Text representation of the JSON data
    """
    # Check if we've reached max depth
    if current_depth >= max_depth:
        return f"{prefix}[Nested content truncated due to depth limit]\n"
    
    # Handle different types
    if isinstance(data, dict):
        text = ""
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                text += f"{prefix}{key}:\n"
                text += json_to_text(value, prefix + "  ", max_depth, current_depth + 1)
            else:
                text += f"{prefix}{key}: {value}\n"
        return text
    
    elif isinstance(data, list):
        text = ""
        # For short lists of primitives, condense to one line
        if len(data) <= 10 and all(not isinstance(item, (dict, list)) for item in data):
            items_str = ", ".join(str(item) for item in data)
            return f"{prefix}[{items_str}]\n"
        else:
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    text += f"{prefix}Item {i}:\n"
                    text += json_to_text(item, prefix + "  ", max_depth, current_depth + 1)
                else:
                    text += f"{prefix}Item {i}: {item}\n"
            return text
    
    else:
        return f"{prefix}{data}\n"
