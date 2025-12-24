# -*- coding: utf-8 -*-
"""
Dependency Checker and Installer
=================================

Automatically checks for and installs missing Python dependencies
for JW zijn babbeldoos application.
"""

import sys
import subprocess
import logging
from typing import List, Tuple, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Required dependencies with pip package names
REQUIRED_DEPENDENCIES = {
    # Module name: (pip package name, description)
    'flask': ('flask', 'Web framework for chat interface'),
    'requests': ('requests', 'HTTP library for Ollama communication'),
    'psycopg2': ('psycopg2-binary', 'PostgreSQL database adapter'),
    'pypdf': ('pypdf', 'PDF text extraction'),
    'docx': ('python-docx', 'DOCX text extraction'),
}


def check_module(module_name: str) -> bool:
    """
    Check if a Python module is installed.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        True if module is installed, False otherwise
    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def install_package(pip_name: str) -> Tuple[bool, str]:
    """
    Install a Python package using pip.
    
    Args:
        pip_name: Name of the package in pip
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        logger.info(f"Installing {pip_name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully installed {pip_name}")
            return True, ""
        else:
            error_msg = result.stderr or result.stdout
            logger.error(f"Failed to install {pip_name}: {error_msg}")
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "Installation timed out after 120 seconds"
        logger.error(f"Failed to install {pip_name}: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to install {pip_name}: {error_msg}")
        return False, error_msg


def check_and_install_dependencies() -> Tuple[bool, List[str]]:
    """
    Check for missing dependencies and install them.
    
    Returns:
        Tuple of (all_installed, list_of_failures)
    """
    logger.info("=" * 70)
    logger.info("CHECKING DEPENDENCIES")
    logger.info("=" * 70)
    
    missing = []
    installed = []
    failed = []
    
    # First pass: Check what's missing
    logger.info("\nChecking installed packages...")
    for module_name, (pip_name, description) in REQUIRED_DEPENDENCIES.items():
        if check_module(module_name):
            logger.info(f"  OK {module_name:12} - {description}")
            installed.append(module_name)
        else:
            logger.warning(f"  MISSING {module_name:12} - {description}")
            missing.append((module_name, pip_name, description))
    
    # If nothing missing, we're done
    if not missing:
        logger.info("\n" + "=" * 70)
        logger.info("All dependencies are installed!")
        logger.info("=" * 70)
        return True, []
    
    # Second pass: Install missing packages
    logger.info(f"\n{len(missing)} package(s) need to be installed")
    logger.info("=" * 70)
    
    for module_name, pip_name, description in missing:
        logger.info(f"\nInstalling {module_name} ({pip_name})...")
        logger.info(f"  Purpose: {description}")
        
        success, error = install_package(pip_name)
        
        if success:
            # Verify installation
            if check_module(module_name):
                logger.info(f"  Verified: {module_name} is now available")
                installed.append(module_name)
            else:
                logger.error(f"  ERROR: {module_name} still not available after install")
                failed.append((module_name, "Installation succeeded but module not found"))
        else:
            failed.append((module_name, error))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("DEPENDENCY CHECK SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Successfully installed: {len(installed)}")
    logger.info(f"Failed installations:   {len(failed)}")
    
    if failed:
        logger.error("\nFailed packages:")
        for module_name, error in failed:
            pip_name = REQUIRED_DEPENDENCIES[module_name][0]
            logger.error(f"  - {module_name} ({pip_name})")
            logger.error(f"    Error: {error[:100]}")
        
        logger.error("\nManual installation required:")
        for module_name, _ in failed:
            pip_name = REQUIRED_DEPENDENCIES[module_name][0]
            logger.error(f"  pip install {pip_name}")
        
        logger.info("=" * 70)
        return False, [m for m, _ in failed]
    else:
        logger.info("\nAll dependencies successfully installed!")
        logger.info("=" * 70)
        return True, []


def check_python_version() -> bool:
    """
    Check if Python version is compatible (>= 3.8).
    
    Returns:
        True if compatible, False otherwise
    """
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("=" * 70)
        logger.error("INCOMPATIBLE PYTHON VERSION")
        logger.error("=" * 70)
        logger.error(f"Current version: {version.major}.{version.minor}.{version.micro}")
        logger.error("Required version: 3.8 or higher")
        logger.error("\nPlease upgrade Python:")
        logger.error("  https://www.python.org/downloads/")
        logger.error("=" * 70)
        return False
    
    logger.info(f"Python version: {version.major}.{version.minor}.{version.micro} (compatible)")
    return True


def check_pip_available() -> bool:
    """
    Check if pip is available.
    
    Returns:
        True if pip is available, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"pip is available: {result.stdout.strip()}")
            return True
        else:
            logger.error("pip is not available")
            return False
    except Exception as e:
        logger.error(f"Error checking pip: {e}")
        return False


def upgrade_pip() -> bool:
    """
    Upgrade pip to latest version.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Upgrading pip to latest version...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("pip upgraded successfully")
            return True
        else:
            logger.warning(f"pip upgrade failed (non-critical): {result.stderr}")
            return False
    except Exception as e:
        logger.warning(f"pip upgrade failed (non-critical): {e}")
        return False


def main() -> bool:
    """
    Main dependency check routine.
    
    Returns:
        True if all dependencies are satisfied, False otherwise
    """
    print()
    logger.info("=" * 70)
    logger.info("JW zijn babbeldoos - Dependency Checker")
    logger.info("=" * 70)
    print()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip_available():
        logger.error("\npip is required but not available")
        logger.error("Please install pip:")
        logger.error("  https://pip.pypa.io/en/stable/installation/")
        return False
    
    # Optionally upgrade pip
    upgrade_pip()
    
    print()
    
    # Check and install dependencies
    success, failed = check_and_install_dependencies()
    
    if not success:
        logger.error("\nSome dependencies could not be installed automatically")
        logger.error("Please install them manually and try again")
        return False
    
    return True


if __name__ == "__main__":
    try:
        if main():
            logger.info("\nAll dependencies satisfied! You can now run the application.")
            sys.exit(0)
        else:
            logger.error("\nDependency check failed. Please resolve the issues above.")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n\nDependency check interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\nUnexpected error during dependency check: {e}", exc_info=True)
        sys.exit(1)
