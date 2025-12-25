# -*- coding: utf-8 -*-
"""
JW zijn babbeldoos - Web Application Launcher
==============================================

Simplified launcher that starts the web interface directly.
All functionality is now available through the web UI.

Author: JW
Version: 3.0.0
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add current directory to path for imports
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(CURRENT_DIR / "tests"))


def check_dependencies():
    """Quick dependency check before starting."""
    print("Checking dependencies...")
    
    from tests.check_dependencies import check_and_install_dependencies, check_python_version
    
    # Check Python version first
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    success, failed = check_and_install_dependencies()
    if not success:
        print("\n⚠️  Some dependencies could not be installed.")
        print("Please install them manually:")
        for module in failed:
            print(f"  pip install {module}")
        sys.exit(1)
    
    print("✓ All dependencies satisfied!\n")


def show_startup_banner():
    """Display startup banner with information."""
    print("=" * 70)
    print("    JW zijn babbeldoos - AI Document Chat System")
    print("=" * 70)
    print()
    print("🚀 Starting web interface...")
    print()
    print("📋 Features available:")
    print("   • Chat Interface - RAG mode & Direct LLM mode")
    print("   • Document Management - View and manage indexed documents")
    print("   • Document Indexing - Index new documents from directories")
    print("   • Storage Analysis - Analyze local storage and find documents")
    print("   • Model Management - Browse, download, and manage LLM models")
    print("   • RAG Evaluation - Test and evaluate retrieval performance")
    print("   • Settings & Deployment - Configure and deploy the system")
    print()
    print("=" * 70)
    print()
    print("🌐 Web interface will be available at: http://127.0.0.1:5000")
    print()
    print("💡 Navigate using the sidebar menu")
    print("⏹  Press Ctrl+C to stop the server")
    print()
    print("=" * 70)
    print()


def main():
    """Main entry point - Launch web interface."""
    try:
        # Check dependencies
        check_dependencies()
        
        # Show startup information
        show_startup_banner()
        
        # Import and start web server
        try:
            from WhereSpaceChat import main as start_web_server
            logger.info("Starting web server...")
            start_web_server()
            
        except ImportError as e:
            logger.error(f"Failed to import WhereSpaceChat: {e}")
            logger.error("Make sure all required modules are installed.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹  Server stopped by user")
        print("Thank you for using JW zijn babbeldoos!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
