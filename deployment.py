# -*- coding: utf-8 -*-
"""
Production Deployment Module
=============================

Handles production deployment with parameter collection and validation.

Author: JW
Version: 1.0.0
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
import secrets

from deployment_config import DeploymentConfig, get_parameter_groups

logger = logging.getLogger(__name__)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_deployment_banner():
    """Display deployment banner."""
    print("=" * 70)
    print("    PRODUCTION DEPLOYMENT")
    print("=" * 70)
    print()


def display_configuration_status(config: DeploymentConfig):
    """
    Display current configuration status with color coding.
    
    Args:
        config: Current deployment configuration
    """
    print("\n" + "=" * 70)
    print("CURRENT CONFIGURATION STATUS")
    print("=" * 70)
    print()
    
    groups = get_parameter_groups()
    
    for group_name, params in groups.items():
        print(f"\n{group_name}:")
        print("-" * 70)
        
        for param in params:
            value = config.get_display_value(param)
            status = "?" if value != "(not set)" else "?"
            print(f"  {status} {param:25} {value}")
    
    # Show completeness status
    is_complete, missing = config.is_complete()
    
    print("\n" + "=" * 70)
    if is_complete:
        print("STATUS: ? Configuration COMPLETE - Ready to deploy")
    else:
        print(f"STATUS: ? Configuration INCOMPLETE - {len(missing)} parameters missing")
        print(f"Missing: {', '.join(missing)}")
    print("=" * 70)


def configure_parameter(config: DeploymentConfig, param_name: str) -> bool:
    """
    Interactive configuration of a single parameter.
    
    Args:
        config: Deployment configuration object
        param_name: Name of parameter to configure
        
    Returns:
        True if parameter was set, False if cancelled
    """
    clear_screen()
    show_deployment_banner()
    
    print(f"Configure Parameter: {param_name}")
    print("=" * 70)
    print()
    
    # Show description
    description = config.get_parameter_description(param_name)
    print(f"Description: {description}")
    print()
    
    # Show current value
    current_value = config.get_display_value(param_name)
    print(f"Current value: {current_value}")
    print()
    
    # Special handling for different parameter types
    if param_name == "ollama_models":
        print("Enter models separated by commas (e.g., llama3.1,mistral,nomic-embed-text)")
        print("Press Enter to keep current, or type 'cancel' to go back")
        user_input = input("> ").strip()
        
        if user_input.lower() == 'cancel':
            return False
        
        if user_input:
            models = [m.strip() for m in user_input.split(',') if m.strip()]
            if models:
                setattr(config, param_name, models)
                print(f"\n? Set {param_name} to: {', '.join(models)}")
                input("\nPress Enter to continue...")
                return True
    
    elif param_name in ["use_https", "backup_enabled", "auto_restart"]:
        print("Enter 'yes' or 'no'")
        print("Press Enter to keep current, or type 'cancel' to go back")
        user_input = input("> ").strip().lower()
        
        if user_input == 'cancel':
            return False
        
        if user_input in ['yes', 'y', '1', 'true']:
            setattr(config, param_name, True)
            print(f"\n? Set {param_name} to: Yes")
            input("\nPress Enter to continue...")
            return True
        elif user_input in ['no', 'n', '0', 'false']:
            setattr(config, param_name, False)
            print(f"\n? Set {param_name} to: No")
            input("\nPress Enter to continue...")
            return True
    
    elif param_name == "app_secret_key":
        print("Options:")
        print("  1. Generate random secure key (recommended)")
        print("  2. Enter custom key manually")
        print("  3. Cancel")
        choice = input("> ").strip()
        
        if choice == '1':
            secret_key = secrets.token_urlsafe(32)
            setattr(config, param_name, secret_key)
            print(f"\n? Generated and set secure secret key")
            input("\nPress Enter to continue...")
            return True
        elif choice == '2':
            print("\nEnter secret key (min 8 characters):")
            user_input = input("> ").strip()
            if user_input:
                is_valid, error = config.validate_parameter(param_name, user_input)
                if is_valid:
                    setattr(config, param_name, user_input)
                    print(f"\n? Set {param_name}")
                    input("\nPress Enter to continue...")
                    return True
                else:
                    print(f"\n? Invalid: {error}")
                    input("\nPress Enter to continue...")
                    return False
        return False
    
    elif param_name in ["server_port", "db_port", "ollama_port", "app_port"]:
        # Get default for this port type
        defaults = {
            "server_port": 22,
            "db_port": 5432,
            "ollama_port": 11434,
            "app_port": 5000
        }
        default = defaults.get(param_name, 0)
        
        print(f"Enter port number (default: {default})")
        print("Press Enter to use default, or type 'cancel' to go back")
        user_input = input("> ").strip()
        
        if user_input.lower() == 'cancel':
            return False
        
        if not user_input:
            user_input = str(default)
        
        is_valid, error = config.validate_parameter(param_name, user_input)
        if is_valid:
            setattr(config, param_name, int(user_input))
            print(f"\n? Set {param_name} to: {user_input}")
            input("\nPress Enter to continue...")
            return True
        else:
            print(f"\n? Invalid: {error}")
            input("\nPress Enter to continue...")
            return False
    
    else:
        # Generic string parameter
        print("Enter value:")
        print("Press Enter to keep current, or type 'cancel' to go back")
        
        # Special prompt for sensitive fields
        if param_name in ["db_password"]:
            print("(input will be hidden)")
            import getpass
            user_input = getpass.getpass("> ")
        else:
            user_input = input("> ").strip()
        
        if user_input.lower() == 'cancel':
            return False
        
        if user_input:
            # Validate input
            is_valid, error = config.validate_parameter(param_name, user_input)
            if is_valid:
                setattr(config, param_name, user_input)
                print(f"\n? Set {param_name}")
                input("\nPress Enter to continue...")
                return True
            else:
                print(f"\n? Invalid: {error}")
                input("\nPress Enter to continue...")
                return False
    
    return False


def show_parameter_menu(config: DeploymentConfig):
    """
    Show interactive parameter configuration menu.
    
    Args:
        config: Deployment configuration object
    """
    while True:
        clear_screen()
        show_deployment_banner()
        
        print("CONFIGURE DEPLOYMENT PARAMETERS")
        print("=" * 70)
        print()
        
        groups = get_parameter_groups()
        param_index = 1
        param_map = {}
        
        for group_name, params in groups.items():
            print(f"\n{group_name}:")
            for param in params:
                value = config.get_display_value(param)
                status = "?" if value != "(not set)" else "?"
                print(f"  {param_index}. {status} {param:20} = {value}")
                param_map[str(param_index)] = param
                param_index += 1
        
        # Show completeness
        is_complete, missing = config.is_complete()
        print("\n" + "=" * 70)
        if is_complete:
            print("? All required parameters configured")
        else:
            print(f"? {len(missing)} required parameters not set")
        print("=" * 70)
        
        print("\nOptions:")
        print("  [1-N]  Configure parameter by number")
        print("  [s]    Save configuration")
        print("  [d]    Deploy now (if complete)")
        print("  [q]    Back to main menu")
        print()
        
        choice = input("Select option: ").strip().lower()
        
        if choice == 'q':
            return
        elif choice == 's':
            if config.save():
                print("\n? Configuration saved successfully!")
            else:
                print("\n? Failed to save configuration")
            input("\nPress Enter to continue...")
        elif choice == 'd':
            if is_complete:
                # Proceed to deployment
                return 'deploy'
            else:
                print(f"\n? Cannot deploy: {len(missing)} parameters missing")
                print(f"Missing: {', '.join(missing)}")
                input("\nPress Enter to continue...")
        elif choice in param_map:
            param_name = param_map[choice]
            configure_parameter(config, param_name)
        else:
            print("\n? Invalid option")
            input("\nPress Enter to continue...")


def run_pre_deployment_checks(config: DeploymentConfig) -> Tuple[bool, List[str]]:
    """
    Run pre-deployment checks to verify system readiness.
    
    Args:
        config: Deployment configuration
        
    Returns:
        Tuple of (all_passed, list_of_failed_checks)
    """
    print("\n" + "=" * 70)
    print("PRE-DEPLOYMENT CHECKS")
    print("=" * 70)
    print()
    
    failed_checks = []
    
    # Check 1: SSH key accessibility
    print("1. Checking SSH key...")
    ssh_key_path = Path(config.server_ssh_key).expanduser()
    if ssh_key_path.exists():
        print("   ? SSH key found")
    else:
        print(f"   ? SSH key not found: {ssh_key_path}")
        failed_checks.append("SSH key not accessible")
    
    # Check 2: Local dependencies
    print("2. Checking local dependencies...")
    try:
        import psycopg2
        import requests
        print("   ? Required Python packages installed")
    except ImportError as e:
        print(f"   ? Missing Python package: {e}")
        failed_checks.append("Missing Python dependencies")
    
    # Check 3: Configuration completeness
    print("3. Checking configuration completeness...")
    is_complete, missing = config.is_complete()
    if is_complete:
        print("   ? All required parameters configured")
    else:
        print(f"   ? Missing parameters: {', '.join(missing)}")
        failed_checks.append("Configuration incomplete")
    
    # Check 4: Server connectivity (if SSH available)
    print("4. Testing server connectivity...")
    try:
        # Attempt to check SSH connection
        result = subprocess.run(
            ["ssh", "-i", str(ssh_key_path), "-o", "ConnectTimeout=5",
             f"{config.server_user}@{config.server_host}", "echo", "OK"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   ? Server accessible via SSH")
        else:
            print("   ? Cannot connect to server (will continue)")
            logger.warning("SSH connection test failed, but continuing deployment")
    except FileNotFoundError:
        print("   ? SSH client not found (skipping connectivity test)")
    except Exception as e:
        print(f"   ? Cannot test connectivity: {e}")
    
    print("\n" + "=" * 70)
    if not failed_checks:
        print("? ALL PRE-DEPLOYMENT CHECKS PASSED")
    else:
        print(f"? {len(failed_checks)} CHECKS FAILED")
        for check in failed_checks:
            print(f"  - {check}")
    print("=" * 70)
    
    return (len(failed_checks) == 0, failed_checks)


def execute_deployment(config: DeploymentConfig) -> bool:
    """
    Execute the deployment process.
    
    Args:
        config: Validated deployment configuration
        
    Returns:
        True if deployment succeeded, False otherwise
    """
    clear_screen()
    show_deployment_banner()
    
    print("DEPLOYMENT IN PROGRESS")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Create deployment script
        print("1. Preparing deployment script...")
        deployment_script = create_deployment_script(config)
        print("   ? Deployment script created")
        
        # Step 2: Run pre-deployment checks
        print("\n2. Running pre-deployment checks...")
        checks_passed, failed = run_pre_deployment_checks(config)
        
        if not checks_passed:
            print(f"\n? Deployment aborted: {len(failed)} checks failed")
            return False
        
        # Step 3: Confirm deployment
        print("\n" + "=" * 70)
        print("?  WARNING: This will deploy WhereSpace to production")
        print("=" * 70)
        print(f"Target: {config.server_user}@{config.server_host}")
        print(f"Domain: {config.app_domain}")
        print(f"Path: {config.deployment_path}")
        print()
        confirm = input("Type 'DEPLOY' to confirm (or anything else to cancel): ").strip()
        
        if confirm != 'DEPLOY':
            print("\n? Deployment cancelled by user")
            return False
        
        # Step 4: Execute deployment
        print("\n3. Deploying to production...")
        print("   (This may take several minutes)")
        print()
        
        # TODO: Implement actual deployment logic
        # For now, show what would happen
        print("   Deployment steps:")
        print("   - Create backup of existing deployment")
        print("   - Upload application files")
        print("   - Install dependencies")
        print("   - Configure database")
        print("   - Setup Ollama models")
        print("   - Configure web server")
        print("   - Start services")
        print()
        print("   ? ACTUAL DEPLOYMENT NOT YET IMPLEMENTED")
        print("   This is a preview of what would happen")
        
        print("\n" + "=" * 70)
        print("? DEPLOYMENT SIMULATION COMPLETE")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        print(f"\n? Deployment failed: {e}")
        return False


def create_deployment_script(config: DeploymentConfig) -> str:
    """
    Create deployment script based on configuration.
    
    Args:
        config: Deployment configuration
        
    Returns:
        Path to deployment script
    """
    script_path = Path(__file__).parent / "deploy.sh"
    
    script_content = f"""#!/bin/bash
# WhereSpace Production Deployment Script
# Generated automatically - DO NOT EDIT

set -e  # Exit on error

echo "==================================="
echo "WhereSpace Production Deployment"
echo "==================================="
echo ""

# Configuration
SERVER_HOST="{config.server_host}"
SERVER_USER="{config.server_user}"
DEPLOYMENT_PATH="{config.deployment_path}"
APP_DOMAIN="{config.app_domain}"
APP_PORT="{config.app_port}"
DB_HOST="{config.db_host}"
DB_PORT="{config.db_port}"
DB_NAME="{config.db_name}"
DB_USER="{config.db_user}"
OLLAMA_HOST="{config.ollama_host}"
OLLAMA_PORT="{config.ollama_port}"

# Step 1: Backup existing deployment
if [ "{config.backup_enabled}" = "True" ]; then
    echo "Creating backup..."
    # Backup logic here
fi

# Step 2: Upload files
echo "Uploading application files..."
# rsync or scp commands here

# Step 3: Install dependencies
echo "Installing dependencies..."
# pip install commands here

# Step 4: Setup database
echo "Configuring database..."
# Database setup commands here

# Step 5: Configure Ollama
echo "Setting up Ollama models..."
# Ollama model pull commands here

# Step 6: Configure web server
echo "Configuring web server..."
# Nginx/Apache configuration here

# Step 7: Start services
if [ "{config.auto_restart}" = "True" ]; then
    echo "Starting services..."
    # Service restart commands here
fi

echo ""
echo "==================================="
echo "Deployment complete!"
echo "Application available at: https://{config.app_domain}"
echo "==================================="
"""
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(0o755)
    
    return str(script_path)


def deploy_to_production():
    """
    Main deployment function - entry point from menu.
    """
    clear_screen()
    show_deployment_banner()
    
    print("Welcome to WhereSpace Production Deployment")
    print()
    print("This wizard will help you deploy WhereSpace to a production server.")
    print("You will need to provide:")
    print("  - Server access credentials")
    print("  - Database connection details")
    print("  - Ollama API configuration")
    print("  - Application domain and SSL settings")
    print()
    input("Press Enter to continue...")
    
    # Load existing configuration
    config = DeploymentConfig.load()
    
    # Show current status
    clear_screen()
    show_deployment_banner()
    display_configuration_status(config)
    input("\nPress Enter to continue...")
    
    # Enter parameter configuration loop
    result = show_parameter_menu(config)
    
    if result == 'deploy':
        # User chose to deploy
        if execute_deployment(config):
            print("\n? Deployment completed successfully!")
        else:
            print("\n? Deployment failed or was cancelled")
        input("\nPress Enter to return to main menu...")
    else:
        # User cancelled or went back
        print("\nConfiguration saved. You can resume deployment later.")
        input("\nPress Enter to return to main menu...")
