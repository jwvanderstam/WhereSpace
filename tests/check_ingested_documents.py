# -*- coding: utf-8 -*-
"""
Check Ingested Documents
========================

Quick script to check if any documents are already in the database.
"""

import sys

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("ERROR: psycopg2 not installed")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)

# Configuration
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "vectordb"
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"
PG_TABLE = "documents"

def main():
    print("=" * 60)
    print("Checking for Ingested Documents")
    print("=" * 60)
    print()
    
    try:
        # Connect to database
        print(f"Connecting to {PG_HOST}:{PG_PORT}/{PG_DATABASE}...")
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
            connect_timeout=5
        )
        print("? Connected\n")
        
        with conn.cursor() as cur:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [PG_TABLE])
            
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                print(f"? Table '{PG_TABLE}' does not exist")
                print("  No documents have been ingested yet.")
                print("  Run WhereSpace.py to start ingestion.")
                return
            
            print(f"? Table '{PG_TABLE}' exists\n")
            
            # Get total counts
            cur.execute(sql.SQL("""
                SELECT 
                    COUNT(*) as total_chunks,
                    COUNT(DISTINCT file_path) as total_documents
                FROM {};
            """).format(sql.Identifier(PG_TABLE)))
            
            total_chunks, total_documents = cur.fetchone()
            
            print(f"?? Statistics:")
            print(f"   Total Documents: {total_documents:,}")
            print(f"   Total Chunks:    {total_chunks:,}")
            print()
            
            if total_documents == 0:
                print("? No documents found in database")
                print("  The table exists but is empty.")
                print("  Run WhereSpace.py to ingest documents.")
                return
            
            # Get document statistics
            cur.execute(sql.SQL("""
                SELECT 
                    file_type,
                    COUNT(DISTINCT file_path) as doc_count,
                    COUNT(*) as chunk_count
                FROM {}
                GROUP BY file_type
                ORDER BY doc_count DESC;
            """).format(sql.Identifier(PG_TABLE)))
            
            file_types = cur.fetchall()
            
            print("?? Documents by Type:")
            for file_type, doc_count, chunk_count in file_types:
                avg_chunks = chunk_count / doc_count if doc_count > 0 else 0
                print(f"   {file_type:8} {doc_count:4} docs, {chunk_count:5} chunks (avg {avg_chunks:.1f} chunks/doc)")
            print()
            
            # Get recent documents
            cur.execute(sql.SQL("""
                SELECT DISTINCT ON (file_path)
                    file_name,
                    file_type,
                    created_at,
                    (SELECT COUNT(*) FROM {} d2 WHERE d2.file_path = d1.file_path) as chunks
                FROM {} d1
                ORDER BY file_path, created_at DESC
                LIMIT 10;
            """).format(sql.Identifier(PG_TABLE), sql.Identifier(PG_TABLE)))
            
            recent_docs = cur.fetchall()
            
            print("?? Sample Documents (first 10):")
            for i, (file_name, file_type, created_at, chunks) in enumerate(recent_docs, 1):
                print(f"   {i:2}. [{file_type:4}] {file_name} ({chunks} chunks)")
            print()
            
            # Get date range
            cur.execute(sql.SQL("""
                SELECT 
                    MIN(created_at) as first_ingested,
                    MAX(created_at) as last_ingested
                FROM {};
            """).format(sql.Identifier(PG_TABLE)))
            
            first_time, last_time = cur.fetchone()
            
            if first_time and last_time:
                print("??  Ingestion Timeline:")
                print(f"   First document: {first_time}")
                print(f"   Last document:  {last_time}")
                
                duration = (last_time - first_time).total_seconds()
                if duration > 0:
                    docs_per_min = (total_documents / duration) * 60
                    print(f"   Duration:       {duration:.0f} seconds")
                    print(f"   Rate:           {docs_per_min:.1f} docs/min")
            print()
            
            # Get oldest 5 documents (by modification time)
            cur.execute(sql.SQL("""
                SELECT DISTINCT ON (file_path)
                    file_name,
                    file_type,
                    modified_time
                FROM {}
                ORDER BY file_path, modified_time ASC
                LIMIT 5;
            """).format(sql.Identifier(PG_TABLE)))
            
            oldest_docs = cur.fetchall()
            
            print("???  Oldest Documents (by file modification time):")
            from datetime import datetime
            for i, (file_name, file_type, mtime) in enumerate(oldest_docs, 1):
                mod_date = datetime.fromtimestamp(mtime)
                print(f"   {i}. [{file_type:4}] {file_name} (modified: {mod_date.strftime('%Y-%m-%d')})")
            print()
            
            print("=" * 60)
            print("? Database contains ingested documents")
            print("  Documents are ready for querying via WhereSpaceChat.py")
            print("=" * 60)
            
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"? Connection error: {e}")
        print("\nTroubleshooting:")
        print("  1. Is PostgreSQL running?")
        print("  2. Is the database 'vectordb' created?")
        print("  3. Are the credentials correct?")
    except Exception as e:
        print(f"? Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
