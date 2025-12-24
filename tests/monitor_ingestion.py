# -*- coding: utf-8 -*-
"""
Real-time Ingestion Monitor
===========================

Monitor the progress of document ingestion by watching the database.
Run this in a separate terminal while ingestion is running.
"""

import sys
import time
from datetime import datetime

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed")
    sys.exit(1)

# Configuration
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "vectordb"
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"
PG_TABLE = "documents"

def clear_screen():
    """Clear terminal screen"""
    print("\033[2J\033[H", end="")

def get_stats(conn):
    """Get ingestion statistics"""
    with conn.cursor() as cur:
        # Total chunks and documents
        cur.execute(f"""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT file_path) as total_documents
            FROM {PG_TABLE};
        """)
        total_chunks, total_documents = cur.fetchone()
        
        # Recent activity (last 60 seconds)
        cur.execute(f"""
            SELECT COUNT(*) 
            FROM {PG_TABLE} 
            WHERE created_at > NOW() - INTERVAL '60 seconds';
        """)
        recent_chunks = cur.fetchone()[0]
        
        # Last inserted document
        cur.execute(f"""
            SELECT file_name, created_at, chunk_index
            FROM {PG_TABLE}
            ORDER BY created_at DESC
            LIMIT 1;
        """)
        last_doc = cur.fetchone()
        
        # File type distribution
        cur.execute(f"""
            SELECT file_type, COUNT(DISTINCT file_path) as count
            FROM {PG_TABLE}
            GROUP BY file_type
            ORDER BY count DESC
            LIMIT 5;
        """)
        file_types = cur.fetchall()
        
        return {
            'total_chunks': total_chunks,
            'total_documents': total_documents,
            'recent_chunks': recent_chunks,
            'last_doc': last_doc,
            'file_types': file_types
        }

def main():
    """Main monitoring loop"""
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        print("Connected! Monitoring ingestion...\n")
        print("Press Ctrl+C to stop\n")
        time.sleep(2)
        
        previous_chunks = 0
        start_time = time.time()
        
        while True:
            try:
                stats = get_stats(conn)
                
                # Clear screen and display
                clear_screen()
                
                print("=" * 60)
                print(f"📊 WhereSpace Ingestion Monitor - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)
                print()
                
                # Overall stats
                print(f"📁 Total Documents: {stats['total_documents']:,}")
                print(f"📄 Total Chunks:    {stats['total_chunks']:,}")
                print()
                
                # Activity
                chunks_per_min = (stats['total_chunks'] - previous_chunks) / (60 if previous_chunks > 0 else 1)
                print(f"⚡ Activity (last 60s): {stats['recent_chunks']:,} chunks")
                print(f"📈 Average Rate:        {chunks_per_min:.1f} chunks/min")
                print()
                
                # Last document
                if stats['last_doc']:
                    file_name, created_at, chunk_idx = stats['last_doc']
                    time_ago = (datetime.now().replace(tzinfo=None) - created_at.replace(tzinfo=None)).seconds
                    print(f"🔄 Last Activity:")
                    print(f"   File: {file_name}")
                    print(f"   Chunk: {chunk_idx}")
                    print(f"   Time: {time_ago}s ago")
                    
                    # Warning if no activity
                    if time_ago > 120:
                        print()
                        print("⚠️  WARNING: No activity for over 2 minutes!")
                        print("   Ingestion may be hung. Check:")
                        print("   - Ollama is running: curl http://localhost:11434/api/tags")
                        print("   - Python process is still running")
                        print("   - PostgreSQL logs for errors")
                print()
                
                # File types
                if stats['file_types']:
                    print(f"📋 Documents by Type:")
                    for file_type, count in stats['file_types']:
                        print(f"   {file_type:8} {count:,} documents")
                print()
                
                # Runtime
                runtime = int(time.time() - start_time)
                print(f"⏱️  Monitoring for: {runtime // 60}m {runtime % 60}s")
                print()
                print("=" * 60)
                
                previous_chunks = stats['total_chunks']
                
                # Update every 5 seconds
                time.sleep(5)
                
            except psycopg2.Error as e:
                print(f"Database error: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
