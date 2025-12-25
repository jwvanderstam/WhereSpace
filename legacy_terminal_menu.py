# -*- coding: utf-8 -*-
"""
JW zijn babbeldoos - Legacy Terminal Menu (ARCHIVED)
====================================================

This file contains the old terminal-based menu system.
Kept for reference only - all functionality is now in the web interface.

To use the web interface instead, simply run:
    python main.py

The web interface provides all these features through an intuitive UI:
- Chat Interface (/)
- Document Management (/documents)
- Document Indexing (/ingest)
- Storage Analysis (/storage)
- Model Management (/models)
- RAG Evaluation (/evaluation)
- Settings (/settings)

Author: JW
Version: 2.0.0 (Archived)
Date: 2025-12-25
"""

# NOTE: This code is preserved for reference only
# All functionality has been migrated to the web interface
# See WhereSpaceChat.py and templates/ for the new implementation

import sys
import os
from pathlib import Path
from typing import Optional

# Legacy imports (kept for reference)
# from WhereSpace import scan_storage, display_results, format_size
# from WhereSpace import ingest_documents_to_pgvector, RAG_DOCUMENT_TYPES, MAX_DOCUMENT_SIZE
# from model_manager import (
#     check_ollama_running, list_installed_models, pull_model,
#     delete_model, search_ollama_models, get_model_statistics
# )


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_banner():
    """Display application banner."""
    print("=" * 60)
    print("    JW zijn babbeldoos - AI Document Chat System")
    print("=" * 60)
    print()


def show_menu():
    """Display main menu."""
    print("\n" + "=" * 60)
    print("HOOFDMENU")
    print("=" * 60)
    print()
    print("1. ?? Analyseer lokale opslag")
    print("   - Scan directories voor bestanden")
    print("   - Bekijk storage verdeling")
    print("   - Identificeer documenten voor indexering")
    print()
    print("2. ?? Indexeer documenten")
    print("   - Selecteer directory met documenten")
    print("   - Extract en chunk tekst")
    print("   - Genereer embeddings en sla op")
    print()
    print("3. ?? Start web chat interface")
    print("   - RAG mode: Query geindexeerde documenten")
    print("   - Direct LLM mode: Algemene vragen")
    print("   - Model switcher (Llama, Mistral, Gemma, Qwen)")
    print()
    print("4. ?? Evalueer RAG performance")
    print("   - Test retrieval kwaliteit")
    print("   - Bekijk Hit Rate en MRR metrics")
    print()
    print("5. ?? Bekijk geindexeerde documenten")
    print("   - Toon alle documenten in database")
    print("   - Bekijk chunk counts en details")
    print()
    print("6. ?? Deploy naar productie")
    print("   - Configure deployment parameters")
    print("   - Run pre-deployment checks")
    print("   - Deploy to production server")
    print()
    print("7. ?? Beheer LLM modellen")
    print("   - Bekijk geinstalleerde modellen")
    print("   - Download nieuwe modellen")
    print("   - Verwijder modellen")
    print()
    print("0. ?? Afsluiten")
    print()
    print("=" * 60)


# NOTE: All the individual menu functions (analyze_storage, ingest_documents, etc.)
# have been migrated to the web interface.
# 
# You can find them as:
# - analyze_storage() -> /storage page in web UI + /api/storage/scan endpoint
# - ingest_documents() -> /ingest page in web UI + /api/ingest_directory endpoint
# - view_indexed_documents() -> /documents page in web UI + /api/list_documents endpoint
# - manage_models() -> /models page in web UI + /api/models/* endpoints
# - evaluate_rag() -> /evaluation page in web UI + /api/evaluation/* endpoints
# - deploy_to_production() -> /settings page in web UI + /api/deploy endpoint


if __name__ == "__main__":
    print("=" * 70)
    print("??  NOTICE: This is the archived terminal menu")
    print("=" * 70)
    print()
    print("The terminal menu has been replaced with a modern web interface.")
    print()
    print("To use the new web interface, run:")
    print("    python main.py")
    print()
    print("All functionality is now available through your browser at:")
    print("    http://127.0.0.1:5000")
    print()
    print("=" * 70)
