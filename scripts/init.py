#!/usr/bin/env python
"""
Initialization script for the unstructured RAG system.
Creates necessary directories and initializes the Git repository.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories for the project."""
    # Define directories to create
    directories = [
        "data",
        "data/documents",
        "data/processing",
        "logs",
    ]
    
    # Create directories
    for directory in directories:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), directory)
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")


def init_git_repository(git_url: str = None):
    """
    Initialize Git repository and set remote origin.
    
    Args:
        git_url: Git remote URL
    """
    # Get project root directory
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    try:
        # Check if Git is already initialized
        result = subprocess.run(
            ["git", "status"],
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        
        if result.returncode == 0:
            logger.info("Git repository already initialized")
        else:
            # Initialize Git repository
            subprocess.run(
                ["git", "init"],
                cwd=root_dir,
                check=True,
            )
            logger.info("Initialized Git repository")
        
        # Set remote origin if provided
        if git_url:
            subprocess.run(
                ["git", "remote", "add", "origin", git_url],
                cwd=root_dir,
                check=False,
            )
            logger.info(f"Set remote origin to: {git_url}")
    
    except Exception as e:
        logger.error(f"Error initializing Git repository: {str(e)}")


def create_env_file():
    """Create .env file if it doesn't exist."""
    root_dir = os.path.dirname(os.path.dirname(__file__))
    env_file = os.path.join(root_dir, ".env")
    env_example_file = os.path.join(root_dir, ".env.example")
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example_file):
            # Copy example file
            with open(env_example_file, "r") as src, open(env_file, "w") as dst:
                dst.write(src.read())
            logger.info(f"Created .env file from .env.example")
        else:
            # Create empty file
            with open(env_file, "w") as f:
                f.write("# Environment variables\n")
                f.write("DEEPSEEK_API_KEY=your_api_key_here\n")
            logger.info(f"Created empty .env file")


def main():
    """Main initialization function."""
    logger.info("Initializing unstructured RAG system")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Initialize Git repository
    git_url = "git@github.com:zahurul-islam/unstructured_rag.git"
    init_git_repository(git_url)
    
    logger.info("Initialization completed")


if __name__ == "__main__":
    main()
