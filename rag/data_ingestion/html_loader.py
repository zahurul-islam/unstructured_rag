"""
HTML document loader.
"""

import os
import logging
from typing import Dict, Tuple, Any
import requests
from bs4 import BeautifulSoup
import chardet

# Configure logging
logger = logging.getLogger(__name__)


def load_html(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load an HTML document and extract its text and metadata.
    
    Args:
        file_path: Path to the HTML file
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        # Check if the file path is a URL
        if file_path.startswith(("http://", "https://")):
            return load_html_from_url(file_path)
        
        # Read file as binary first to detect encoding
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            
            # Detect encoding
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
            # Parse HTML
            soup = BeautifulSoup(raw_data, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract all text
        text = soup.get_text(separator=' ', strip=True)
        
        # Extract links
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        # Count images
        image_count = len(soup.find_all('img'))
        
        # Create HTML-specific metadata
        metadata = {
            "title": title,
            "link_count": len(links),
            "image_count": image_count,
            "source_type": "html",
            "encoding": encoding
        }
        
        return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading HTML file: {str(e)}")
        
        # Return empty text with error metadata
        return "", {
            "source_type": "html",
            "extraction_error": str(e),
            "extraction_success": False
        }


def load_html_from_url(url: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load HTML content from a URL.
    
    Args:
        url: URL to fetch HTML from
        
    Returns:
        Tuple containing:
            - Extracted text content (str)
            - Document metadata (Dict[str, Any])
    """
    try:
        # Fetch content from URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract all text
        text = soup.get_text(separator=' ', strip=True)
        
        # Extract links
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        # Count images
        image_count = len(soup.find_all('img'))
        
        # Create HTML-specific metadata
        metadata = {
            "title": title,
            "url": url,
            "link_count": len(links),
            "image_count": image_count,
            "source_type": "html",
            "status_code": response.status_code
        }
        
        return text, metadata
    
    except Exception as e:
        logger.error(f"Error loading HTML from URL: {str(e)}")
        
        # Return empty text with error metadata
        return "", {
            "source_type": "html",
            "url": url,
            "extraction_error": str(e),
            "extraction_success": False
        }
