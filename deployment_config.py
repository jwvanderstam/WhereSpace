# -*- coding: utf-8 -*-
"""
Deployment Configuration Module
================================

Manages production deployment parameters and validation.

Author: JW
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List
import re

logger = logging.getLogger(__name__)

# Configuration file location
CONFIG_FILE = Path(__file__).parent / "config" / "deployment_config.json"


@dataclass
class DeploymentConfig:
    """
    Production deployment configuration with validation.
    
    All parameters required for deploying WhereSpace to production.
    """
    # Server Configuration
    server_host: str = ""
    server_port: int = 0
    server_user: str = ""
    server_ssh_key: str = ""
    
    # Database Configuration
    db_host: str = ""
    db_port: int = 5432
    db_name: str = "vectordb"
    db_user: str = ""
    db_password: str = ""
    
    # Ollama Configuration
    ollama_host: str = ""
    ollama_port: int = 11434
    ollama_models: List[str] = field(default_factory=lambda: ["llama3.1", "nomic-embed-text"])
    
    # Application Configuration
    app_domain: str = ""
    app_port: int = 5000
    app_secret_key: str = ""
    use_https: bool = True
    
    # Deployment Settings
    deployment_path: str = "/opt/wherespace"
    backup_enabled: bool = True
    auto_restart: bool = True
    
    # Optional: Email notifications
    notification_email: str = ""
    
    def is_complete(self) -> tuple[bool, List[str]]:
        """
        Check if all required parameters are set.
        
        Returns:
            Tuple of (is_complete, list_of_missing_params)
        """
        missing = []
        
        # Required server parameters
        if not self.server_host:
            missing.append("server_host")
        if self.server_port <= 0:
            missing.append("server_port")
        if not self.server_user:
            missing.append("server_user")
        if not self.server_ssh_key:
            missing.append("server_ssh_key")
        
        # Required database parameters
        if not self.db_host:
            missing.append("db_host")
        if not self.db_user:
            missing.append("db_user")
        if not self.db_password:
            missing.append("db_password")
        
        # Required Ollama parameters
        if not self.ollama_host:
            missing.append("ollama_host")
        
        # Required app parameters
        if not self.app_domain:
            missing.append("app_domain")
        if not self.app_secret_key:
            missing.append("app_secret_key")
        
        return (len(missing) == 0, missing)
    
    def validate_parameter(self, param_name: str, value: str) -> tuple[bool, str]:
        """
        Validate a single parameter value.
        
        Args:
            param_name: Name of parameter to validate
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if param_name in ["server_host", "db_host", "ollama_host"]:
            # Validate hostname or IP
            if not value:
                return False, "Host cannot be empty"
            # Basic hostname/IP validation
            pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if not re.match(pattern, value):
                return False, "Invalid hostname or IP address"
        
        elif param_name in ["server_port", "db_port", "ollama_port", "app_port"]:
            # Validate port number
            try:
                port = int(value)
                if port < 1 or port > 65535:
                    return False, "Port must be between 1 and 65535"
            except ValueError:
                return False, "Port must be a number"
        
        elif param_name == "server_ssh_key":
            # Validate SSH key path
            if not value:
                return False, "SSH key path cannot be empty"
            key_path = Path(value).expanduser()
            if not key_path.exists():
                return False, f"SSH key file not found: {key_path}"
            if not key_path.is_file():
                return False, f"SSH key path is not a file: {key_path}"
        
        elif param_name == "app_domain":
            # Validate domain name
            if not value:
                return False, "Domain cannot be empty"
            pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
            if not re.match(pattern, value):
                return False, "Invalid domain name"
        
        elif param_name == "notification_email":
            # Validate email (optional)
            if value:  # Only validate if provided
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(pattern, value):
                    return False, "Invalid email address"
        
        elif param_name in ["server_user", "db_user", "db_name"]:
            # Validate username/database name
            if not value:
                return False, f"{param_name} cannot be empty"
            if not re.match(r'^[a-zA-Z0-9_-]+$', value):
                return False, "Only alphanumeric characters, underscore, and hyphen allowed"
        
        elif param_name in ["db_password", "app_secret_key"]:
            # Validate passwords/secrets
            if not value:
                return False, f"{param_name} cannot be empty"
            if len(value) < 8:
                return False, "Must be at least 8 characters"
        
        elif param_name == "deployment_path":
            # Validate deployment path
            if not value:
                return False, "Deployment path cannot be empty"
            if not value.startswith('/'):
                return False, "Deployment path must be absolute (start with /)"
        
        return True, ""
    
    def get_parameter_description(self, param_name: str) -> str:
        """Get human-readable description for a parameter."""
        descriptions = {
            "server_host": "Production server hostname or IP address",
            "server_port": "SSH port for server access (default: 22)",
            "server_user": "SSH username for server access",
            "server_ssh_key": "Path to SSH private key file",
            "db_host": "PostgreSQL database hostname or IP",
            "db_port": "PostgreSQL port (default: 5432)",
            "db_name": "Database name (default: vectordb)",
            "db_user": "Database username",
            "db_password": "Database password",
            "ollama_host": "Ollama API hostname or IP",
            "ollama_port": "Ollama API port (default: 11434)",
            "ollama_models": "Ollama models to install (comma-separated)",
            "app_domain": "Application domain name (e.g., wherespace.example.com)",
            "app_port": "Application port (default: 5000)",
            "app_secret_key": "Flask secret key for session security",
            "use_https": "Enable HTTPS (requires SSL certificate)",
            "deployment_path": "Server directory for application files",
            "backup_enabled": "Enable automatic backups before deployment",
            "auto_restart": "Automatically restart services after deployment",
            "notification_email": "Email for deployment notifications (optional)"
        }
        return descriptions.get(param_name, "No description available")
    
    def save(self) -> bool:
        """
        Save configuration to JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            CONFIG_FILE.parent.mkdir(exist_ok=True)
            
            # Convert to dict, masking sensitive data in logs
            config_dict = asdict(self)
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Deployment configuration saved to {CONFIG_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    @classmethod
    def load(cls) -> 'DeploymentConfig':
        """
        Load configuration from JSON file.
        
        Returns:
            DeploymentConfig instance (empty if file doesn't exist)
        """
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create instance from loaded data
                config = cls(**data)
                logger.info(f"Deployment configuration loaded from {CONFIG_FILE}")
                return config
            else:
                logger.info("No existing deployment configuration found")
                return cls()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return cls()
    
    def get_display_value(self, param_name: str) -> str:
        """
        Get display-friendly value for a parameter (masks sensitive data).
        
        Args:
            param_name: Parameter name
            
        Returns:
            Display string
        """
        value = getattr(self, param_name, None)
        
        # Mask sensitive parameters
        if param_name in ["db_password", "app_secret_key"]:
            if value and len(value) > 0:
                return "?" * 8 + " (set)"
            else:
                return "(not set)"
        
        # Handle lists
        if isinstance(value, list):
            if value:
                return ", ".join(str(v) for v in value)
            else:
                return "(empty)"
        
        # Handle booleans
        if isinstance(value, bool):
            return "Yes" if value else "No"
        
        # Handle empty/default values
        if value == "" or value == 0:
            return "(not set)"
        
        return str(value)


def get_parameter_groups() -> Dict[str, List[str]]:
    """
    Get parameters organized by category.
    
    Returns:
        Dictionary mapping category name to list of parameter names
    """
    return {
        "Server Configuration": [
            "server_host",
            "server_port",
            "server_user",
            "server_ssh_key"
        ],
        "Database Configuration": [
            "db_host",
            "db_port",
            "db_name",
            "db_user",
            "db_password"
        ],
        "Ollama Configuration": [
            "ollama_host",
            "ollama_port",
            "ollama_models"
        ],
        "Application Configuration": [
            "app_domain",
            "app_port",
            "app_secret_key",
            "use_https"
        ],
        "Deployment Settings": [
            "deployment_path",
            "backup_enabled",
            "auto_restart",
            "notification_email"
        ]
    }
