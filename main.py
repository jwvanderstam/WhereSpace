# -*- coding: utf-8 -*-
"""
JW zijn babbeldoos - Main Menu
================================

Unified entry point for all functionality:
1. Analyze local storage
2. Ingest documents 
3. Start web chat interface

Author: JW
Version: 2.0.0
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

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

print("Checking dependencies...")
# Import dependency checker from tests directory
from tests.check_dependencies import check_and_install_dependencies, check_python_version

# Check Python version first
if not check_python_version():
    sys.exit(1)

# Check and install dependencies
success, failed = check_and_install_dependencies()
if not success:
    print("\nSome dependencies could not be installed.")
    print("Please install them manually:")
    for module in failed:
        print(f"  pip install {module}")
    sys.exit(1)

# Import modules
try:
    from WhereSpace import scan_storage, display_results, format_size
    from WhereSpace import ingest_documents_to_pgvector, RAG_DOCUMENT_TYPES, MAX_DOCUMENT_SIZE
    from WhereSpaceChat import main as start_chat_server
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    MODULES_AVAILABLE = False


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
    print("0. ? Afsluiten")
    print()
    print("=" * 60)


def analyze_storage():
    """Option 1: Analyze local storage."""
    clear_screen()
    show_banner()
    print("?? OPSLAG ANALYSE")
    print("=" * 60)
    print()
    
    # Get scan directory
    default_path = Path.home()
    user_input = input(f"Directory om te scannen [{default_path}]: ").strip()
    scan_path = Path(user_input) if user_input else default_path
    
    if not scan_path.exists():
        logger.error(f"Directory bestaat niet: {scan_path}")
        input("\nDruk op Enter om terug te gaan...")
        return
    
    try:
        # Scan
        logger.info(f"Scannen {scan_path}...")
        categories, directories, documents_by_dir = scan_storage(scan_path)
        
        # Display results
        clear_screen()
        show_banner()
        display_results(categories, directories)
        
        # Document summary
        total_docs = sum(len(docs) for docs in documents_by_dir.values())
        print(f"\n?? Gevonden documenten: {total_docs:,}")
        
        if total_docs > 0:
            print(f"   Directories met documenten: {len(documents_by_dir):,}")
            
            # Show top directories
            sorted_dirs = sorted(
                documents_by_dir.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            print("\nTop 5 directories:")
            for i, (dir_path, docs) in enumerate(sorted_dirs, 1):
                print(f"  {i}. [{len(docs):4} docs] {dir_path}")
        
        input("\nDruk op Enter om terug te gaan...")
        
    except Exception as e:
        logger.error(f"Fout bij scannen: {e}")
        input("\nDruk op Enter om terug te gaan...")


def ingest_documents():
    """Option 2: Ingest documents uniformly."""
    clear_screen()
    show_banner()
    print("?? DOCUMENTEN INDEXEREN")
    print("=" * 60)
    print()
    
    # Get directory
    user_input = input("Directory met documenten: ").strip()
    if not user_input:
        logger.info("Geannuleerd")
        input("\nDruk op Enter om terug te gaan...")
        return
    
    dir_path = Path(user_input)
    
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Directory bestaat niet: {dir_path}")
        input("\nDruk op Enter om terug te gaan...")
        return
    
    try:
        # Find documents
        logger.info(f"Zoeken naar documenten in {dir_path}...")
        documents = []
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower().lstrip('.')
                try:
                    file_size = file_path.stat().st_size
                    if ext in RAG_DOCUMENT_TYPES and file_size < MAX_DOCUMENT_SIZE:
                        documents.append(file_path)
                except OSError:
                    continue
        
        if not documents:
            logger.warning("Geen documenten gevonden")
            input("\nDruk op Enter om terug te gaan...")
            return
        
        logger.info(f"? Gevonden {len(documents)} documenten")
        
        # Show file types
        from collections import Counter
        file_types = Counter(f.suffix.lower() for f in documents)
        print("\nBestandstypes:")
        for ext, count in file_types.most_common():
            print(f"  {ext:8} {count:4} bestanden")
        
        # Confirm
        print()
        confirm = input(f"Indexeer deze {len(documents)} documenten? [j/N]: ").strip().lower()
        if confirm != 'j':
            logger.info("Geannuleerd")
            input("\nDruk op Enter om terug te gaan...")
            return
        
        # Ingest
        print()
        logger.info("Start indexering...")
        ingested = ingest_documents_to_pgvector(documents)
        
        print()
        logger.info(f"? Klaar! {ingested} documenten geindexeerd")
        input("\nDruk op Enter om terug te gaan...")
        
    except Exception as e:
        logger.error(f"Fout bij indexeren: {e}", exc_info=True)
        input("\nDruk op Enter om terug te gaan...")


def start_webserver():
    """Option 3: Start web chat interface."""
    clear_screen()
    show_banner()
    print("?? WEB CHAT INTERFACE")
    print("=" * 60)
    print()
    print("Starting JW zijn babbeldoos web interface...")
    print()
    print("Features:")
    print("  ? RAG mode voor document queries")
    print("  ? Direct LLM mode voor algemene vragen")
    print("  ? Model switcher (4 modellen beschikbaar)")
    print("  ? Source citations in antwoorden")
    print("  ? Document management")
    print()
    print("Navigeer naar: http://127.0.0.1:5000")
    print()
    print("Druk Ctrl+C om te stoppen")
    print()
    
    try:
        start_chat_server()
    except KeyboardInterrupt:
        print("\n\n? Webserver gestopt")
        input("\nDruk op Enter om terug te gaan...")


def evaluate_rag():
    """Option 4: Evaluate RAG performance."""
    clear_screen()
    show_banner()
    print("?? RAG EVALUATIE")
    print("=" * 60)
    print()
    
    try:
        # Check if documents exist first
        import psycopg2
        from psycopg2 import sql
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="vectordb",
                user="postgres",
                password="Mutsmuts10"
            )
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(DISTINCT file_path) 
                    FROM documents;
                """)
                doc_count = cur.fetchone()[0]
            
            conn.close()
            
            if doc_count == 0:
                logger.error("Geen documenten gevonden in database!")
                logger.info("Indexeer eerst documenten via optie 2")
                input("\nDruk op Enter om terug te gaan...")
                return
            
            logger.info(f"Gevonden: {doc_count} documenten in database")
            logger.info("Start evaluatie...\n")
            
        except Exception as db_error:
            logger.error(f"Database verbindingsfout: {db_error}")
            logger.info("Controleer of PostgreSQL draait")
            input("\nDruk op Enter om terug te gaan...")
            return
        
        # Import and run evaluation
        import evaluate_rag
        
        # Generate queries from actual documents
        logger.info("Genereer test queries van je documenten...")
        test_queries = evaluate_rag.generate_test_queries_from_documents()
        
        if not test_queries:
            logger.warning("Kon geen test queries genereren")
            logger.info("Mogelijk hebben documenten te weinig inhoud")
            input("\nDruk op Enter om terug te gaan...")
            return
        
        logger.info(f"Gegenereerd: {len(test_queries)} test queries\n")
        
        # Run evaluation
        results = evaluate_rag.evaluate_retrieval(test_queries, show_details=True)
        
        # Show summary
        print("\n" + "=" * 60)
        print("SAMENVATTING")
        print("=" * 60)
        print(f"Documenten getest:     {results.get('stats', {}).get('total_documents', 0)}")
        print(f"Test queries:          {results.get('total_tests', 0)}")
        print(f"Succesvolle queries:   {results.get('hits', 0)}")
        print(f"Hit rate:              {results.get('hit_rate', 0):.1f}%")
        print(f"Gemiddelde similarity: {results.get('avg_similarity', 0):.3f}")
        print("=" * 60)
        
        input("\nDruk op Enter om terug te gaan...")
        
    except ImportError as ie:
        logger.error(f"Module import fout: {ie}")
        logger.info("Installeer ontbrekende modules:")
        logger.info("  pip install psycopg2-binary requests")
        input("\nDruk op Enter om terug te gaan...")
    except Exception as e:
        logger.error(f"Fout bij evaluatie: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        input("\nDruk op Enter om terug te gaan...")


def view_indexed_documents():
    """Option 5: View indexed documents."""
    clear_screen()
    show_banner()
    print("?? GEINDEXEERDE DOCUMENTEN")
    print("=" * 60)
    print()
    
    try:
        import psycopg2
        from psycopg2 import sql
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="vectordb",
            user="postgres",
            password="Mutsmuts10"
        )
        
        with conn.cursor() as cur:
            # Get document stats
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT file_path) as doc_count,
                    COUNT(*) as chunk_count,
                    SUM(file_size) as total_size
                FROM documents;
            """)
            
            doc_count, chunk_count, total_size = cur.fetchone()
            
            print(f"Totaal documenten: {doc_count:,}")
            print(f"Totaal chunks:     {chunk_count:,}")
            print(f"Totale grootte:    {format_size(total_size or 0)}")
            print()
            
            # Get document list
            cur.execute("""
                SELECT DISTINCT ON (file_path)
                    file_name,
                    file_type,
                    file_size,
                    (SELECT COUNT(*) FROM documents d2 WHERE d2.file_path = d1.file_path) as chunks
                FROM documents d1
                ORDER BY file_path, created_at DESC;
            """)
            
            documents = cur.fetchall()
            
            if documents:
                print("Documenten:")
                print("-" * 60)
                for i, (name, ftype, size, chunks) in enumerate(documents, 1):
                    size_str = format_size(size)
                    print(f"{i:3}. [{ftype:5}] {name:40} {size_str:>10} ({chunks} chunks)")
            else:
                print("Geen documenten gevonden")
        
        conn.close()
        input("\nDruk op Enter om terug te gaan...")
        
    except Exception as e:
        logger.error(f"Fout bij ophalen documenten: {e}")
        input("\nDruk op Enter om terug te gaan...")


def main():
    """Main menu loop."""
    if not MODULES_AVAILABLE:
        logger.error("Required modules not available")
        sys.exit(1)
    
    while True:
        try:
            clear_screen()
            show_banner()
            show_menu()
            
            choice = input("Kies een optie [0-5]: ")

            if choice == '1':
                analyze_storage()
            elif choice == '2':
                ingest_documents()
            elif choice == '3':
                start_webserver()
            elif choice == '4':
                evaluate_rag()
            elif choice == '5':
                view_indexed_documents()
            elif choice == '0':
                clear_screen()
                show_banner()
                print("Bedankt voor het gebruiken van JW zijn babbeldoos!")
                print()
                sys.exit(0)
            else:
                print("\n? Ongeldige keuze. Probeer opnieuw.")
                input("Druk op Enter om door te gaan...")
        
        except EOFError:
            # Handle non-interactive mode or closed input stream
            logger.info("\n\nNo input available (non-interactive mode)")
            logger.info("Exiting gracefully...")
            sys.exit(0)
        except KeyboardInterrupt:
            # Handle Ctrl+C during menu input
            logger.info("\n\nInterrupted by user")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n? Programma afgesloten")
        sys.exit(0)
    except EOFError:
        print("\n\n? No input available - exiting")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
