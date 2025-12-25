# -*- coding: utf-8 -*-
"""
LLM Model Management Module
============================

Manages Ollama LLM models: browse, download, and delete.

Author: JW
Version: 1.0.0
"""

import requests
import subprocess
import sys
import logging
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Ollama API endpoints
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_PULL_URL = f"{OLLAMA_BASE_URL}/api/pull"
OLLAMA_DELETE_URL = f"{OLLAMA_BASE_URL}/api/delete"
OLLAMA_SHOW_URL = f"{OLLAMA_BASE_URL}/api/show"


def format_size(bytes_size: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "4.2 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def check_ollama_running() -> bool:
    """
    Check if Ollama service is running.
    
    Returns:
        True if Ollama is accessible, False otherwise
    """
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_installed_models() -> List[Dict]:
    """
    Get list of installed Ollama models.
    
    Returns:
        List of model dictionaries with details
    """
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        if 'models' in data:
            for model in data['models']:
                model_info = {
                    'name': model.get('name', 'Unknown'),
                    'size': model.get('size', 0),
                    'size_formatted': format_size(model.get('size', 0)),
                    'modified': model.get('modified_at', ''),
                    'digest': model.get('digest', ''),
                    'family': extract_model_family(model.get('name', '')),
                }
                models.append(model_info)
        
        return sorted(models, key=lambda x: x['name'])
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error listing models: {e}")
        return []


def extract_model_family(model_name: str) -> str:
    """
    Extract model family from full model name.
    
    Args:
        model_name: Full model name (e.g., "llama3.1:latest")
        
    Returns:
        Model family name (e.g., "llama")
    """
    base_name = model_name.split(':')[0].lower()
    
    if 'llama' in base_name:
        return 'Llama'
    elif 'mistral' in base_name:
        return 'Mistral'
    elif 'gemma' in base_name:
        return 'Gemma'
    elif 'qwen' in base_name:
        return 'Qwen'
    elif 'phi' in base_name:
        return 'Phi'
    elif 'codellama' in base_name:
        return 'CodeLlama'
    elif 'nomic' in base_name:
        return 'Nomic'
    else:
        return 'Other'


def pull_model(model_name: str, show_progress: bool = True) -> Tuple[bool, str]:
    """
    Download/pull a model from Ollama registry.
    
    Args:
        model_name: Name of model to pull (e.g., "llama3.1", "mistral:latest")
        show_progress: Whether to show download progress
        
    Returns:
        Tuple of (success, message)
    """
    try:
        payload = {"name": model_name, "stream": True}
        
        response = requests.post(
            OLLAMA_PULL_URL,
            json=payload,
            stream=True,
            timeout=600  # 10 minute timeout for large models
        )
        response.raise_for_status()
        
        if show_progress:
            print(f"\n?? Downloading {model_name}...")
            print("-" * 60)
        
        last_status = ""
        total_size = 0
        downloaded = 0
        
        for line in response.iter_lines():
            if line:
                try:
                    import json
                    data = json.loads(line)
                    
                    status = data.get('status', '')
                    
                    if 'total' in data and 'completed' in data:
                        total_size = data['total']
                        downloaded = data['completed']
                        
                        if total_size > 0 and show_progress:
                            percent = (downloaded / total_size) * 100
                            downloaded_str = format_size(downloaded)
                            total_str = format_size(total_size)
                            
                            # Progress bar
                            bar_length = 40
                            filled = int(bar_length * downloaded / total_size)
                            bar = '?' * filled + '?' * (bar_length - filled)
                            
                            print(f"\r{bar} {percent:.1f}% ({downloaded_str}/{total_str})", end='', flush=True)
                    
                    elif status != last_status and show_progress:
                        if status:
                            print(f"\n{status}")
                        last_status = status
                        
                except json.JSONDecodeError:
                    continue
        
        if show_progress:
            print("\n" + "-" * 60)
            print(f"? Successfully pulled {model_name}")
        
        return True, f"Model {model_name} installed successfully"
        
    except requests.exceptions.Timeout:
        error_msg = f"Download timeout for {model_name}. The model may be too large or connection is slow."
        logger.error(error_msg)
        return False, error_msg
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error pulling model {model_name}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def delete_model(model_name: str) -> Tuple[bool, str]:
    """
    Delete a model from local Ollama storage.
    
    Args:
        model_name: Full name of model to delete
        
    Returns:
        Tuple of (success, message)
    """
    try:
        payload = {"name": model_name}
        
        response = requests.delete(
            OLLAMA_DELETE_URL,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Model {model_name} deleted successfully"
        else:
            error_msg = f"Failed to delete {model_name}: {response.text}"
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error deleting model {model_name}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def get_model_info(model_name: str) -> Optional[Dict]:
    """
    Get detailed information about a specific model.
    
    Args:
        model_name: Name of model
        
    Returns:
        Dictionary with model details, or None if not found
    """
    try:
        payload = {"name": model_name}
        
        response = requests.post(
            OLLAMA_SHOW_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'modelfile': data.get('modelfile', ''),
                'parameters': data.get('parameters', ''),
                'template': data.get('template', ''),
                'details': data.get('details', {})
            }
        
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting model info: {e}")
        return None


def search_ollama_models(query: str = "") -> List[Dict]:
    """
    Search for available models in Ollama library.
    
    Note: This is a curated list of popular models since Ollama
    doesn't have a public search API yet.
    
    Args:
        query: Search query (filters by name)
        
    Returns:
        List of available models
    """
    # Curated list of popular Ollama models
    popular_models = [
        {
            'name': 'llama3.1',
            'family': 'Llama',
            'description': 'Meta Llama 3.1 - Fast, general purpose (8B params)',
            'size_estimate': '4.7 GB',
            'recommended': True
        },
        {
            'name': 'llama3.1:70b',
            'family': 'Llama',
            'description': 'Meta Llama 3.1 - Larger, more capable (70B params)',
            'size_estimate': '40 GB',
            'recommended': False
        },
        {
            'name': 'mistral',
            'family': 'Mistral',
            'description': 'Mistral 7B - Balanced performance and speed',
            'size_estimate': '4.1 GB',
            'recommended': True
        },
        {
            'name': 'mixtral',
            'family': 'Mistral',
            'description': 'Mixtral 8x7B - Mixture of experts, very capable',
            'size_estimate': '26 GB',
            'recommended': False
        },
        {
            'name': 'gemma2',
            'family': 'Gemma',
            'description': 'Google Gemma 2 - Latest from Google (9B params)',
            'size_estimate': '5.4 GB',
            'recommended': True
        },
        {
            'name': 'gemma2:27b',
            'family': 'Gemma',
            'description': 'Google Gemma 2 - Larger variant (27B params)',
            'size_estimate': '16 GB',
            'recommended': False
        },
        {
            'name': 'qwen2.5',
            'family': 'Qwen',
            'description': 'Alibaba Qwen 2.5 - Strong reasoning (7B params)',
            'size_estimate': '4.7 GB',
            'recommended': True
        },
        {
            'name': 'qwen2.5:32b',
            'family': 'Qwen',
            'description': 'Alibaba Qwen 2.5 - Larger variant (32B params)',
            'size_estimate': '20 GB',
            'recommended': False
        },
        {
            'name': 'phi3',
            'family': 'Phi',
            'description': 'Microsoft Phi-3 - Small but capable (3.8B params)',
            'size_estimate': '2.3 GB',
            'recommended': True
        },
        {
            'name': 'codellama',
            'family': 'CodeLlama',
            'description': 'Meta Code Llama - Specialized for coding',
            'size_estimate': '3.8 GB',
            'recommended': True
        },
        {
            'name': 'codellama:34b',
            'family': 'CodeLlama',
            'description': 'Meta Code Llama - Larger coding model',
            'size_estimate': '19 GB',
            'recommended': False
        },
        {
            'name': 'nomic-embed-text',
            'family': 'Nomic',
            'description': 'Nomic Embed - Text embeddings (required for RAG)',
            'size_estimate': '274 MB',
            'recommended': True
        },
    ]
    
    # Filter by query if provided
    if query:
        query_lower = query.lower()
        filtered = [
            m for m in popular_models
            if query_lower in m['name'].lower() or query_lower in m['description'].lower()
        ]
        return filtered
    
    return popular_models


def get_model_statistics() -> Dict:
    """
    Get statistics about installed models.
    
    Returns:
        Dictionary with model statistics
    """
    models = list_installed_models()
    
    total_size = sum(m['size'] for m in models)
    
    families = {}
    for model in models:
        family = model['family']
        families[family] = families.get(family, 0) + 1
    
    return {
        'total_models': len(models),
        'total_size': total_size,
        'total_size_formatted': format_size(total_size),
        'families': families,
        'models': models
    }


def verify_model_available(model_name: str) -> bool:
    """
    Verify if a specific model is installed and available.
    
    Args:
        model_name: Name of model to check
        
    Returns:
        True if model is installed, False otherwise
    """
    models = list_installed_models()
    
    # Check both exact match and without :latest suffix
    model_names = [m['name'] for m in models]
    
    return (
        model_name in model_names or
        f"{model_name}:latest" in model_names or
        model_name.replace(':latest', '') in [m.replace(':latest', '') for m in model_names]
    )
