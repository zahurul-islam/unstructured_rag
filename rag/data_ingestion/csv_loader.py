"""
CSV document loader.
"""

import os
import logging
from typing import Dict, Tuple, Any, List
import csv
import json
import chardet

# Configure logging
logger = logging.getLogger(__name__)


def load_csv(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a CSV file and convert it to text format.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple containing:
            - Text representation of CSV (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        # Read file as binary first to detect encoding
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            
            # Detect encoding
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        
        # Read CSV with detected encoding
        with open(file_path, 'r', encoding=encoding, newline='') as file:
            # Detect dialect
            dialect = csv.Sniffer().sniff(file.read(1024))
            file.seek(0)
            
            # Read as CSV
            reader = csv.reader(file, dialect)
            rows = list(reader)
            
            if not rows:
                return "", {"source_type": "csv", "row_count": 0, "column_count": 0}
            
            # Extract headers (first row)
            headers = rows[0]
            
            # Convert to list of dictionaries
            data = []
            for row in rows[1:]:
                if len(row) == len(headers):
                    data.append(dict(zip(headers, row)))
            
            # Convert to text representation
            text = csv_to_text(headers, data)
            
            # Create CSV-specific metadata
            metadata = {
                "source_type": "csv",
                "row_count": len(rows) - 1,  # Excluding header
                "column_count": len(headers),
                "columns": headers,
                "encoding": encoding,
                "dialect": dialect.__dict__
            }
            
            return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading CSV file: {str(e)}")
        
        # Try with pandas as fallback
        try:
            return load_csv_with_pandas(file_path)
        except:
            # Return empty text with error metadata
            return "", {
                "source_type": "csv",
                "extraction_error": str(e),
                "extraction_success": False
            }


def csv_to_text(headers: List[str], data: List[Dict[str, str]]) -> str:
    """
    Convert CSV data to a structured text representation.
    
    Args:
        headers: List of column headers
        data: List of dictionaries mapping headers to values
        
    Returns:
        Text representation of the CSV data
    """
    # Start with a description of the CSV
    text = f"CSV with {len(headers)} columns: {', '.join(headers)}.\n\n"
    
    # Add each row as a structured paragraph
    for i, row in enumerate(data):
        text += f"Row {i+1}:\n"
        for header in headers:
            value = row.get(header, "")
            text += f"  {header}: {value}\n"
        text += "\n"
    
    return text


def load_csv_with_pandas(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Fallback method to load a CSV using pandas.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple containing:
            - Text representation of CSV (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        import pandas as pd
        
        # Read CSV with pandas
        df = pd.read_csv(file_path)
        
        # Get headers and data
        headers = df.columns.tolist()
        data = df.to_dict(orient='records')
        
        # Convert to text representation
        text = csv_to_text(headers, data)
        
        # Create CSV-specific metadata
        metadata = {
            "source_type": "csv",
            "extraction_method": "pandas",
            "row_count": len(df),
            "column_count": len(headers),
            "columns": headers,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading CSV with pandas: {str(e)}")
        
        # Return empty text with error metadata
        return "", {
            "source_type": "csv",
            "extraction_error": str(e),
            "extraction_success": False
        }
