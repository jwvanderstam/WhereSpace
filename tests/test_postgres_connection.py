# -*- coding: utf-8 -*-
"""
PostgreSQL Connection Diagnostics
==================================

Quick diagnostic tool to test PostgreSQL connectivity and pgvector setup.
Run this before WhereSpace.py to verify your setup.
"""

import sys
import subprocess

# Try to import psycopg2
try:
    import psycopg2
    from psycopg2 import sql
    print("? psycopg2 module available")
except ImportError:
    print("? psycopg2 not installed")
    print("  Install with: pip install psycopg2-binary")
    sys.exit(1)

# Configuration (update these to match your setup)
PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"

print("\n" + "=" * 60)
print("PostgreSQL Connection Diagnostics")
print("=" * 60)

# Test 1: Connect to postgres database
print("\n[Test 1] Connecting to 'postgres' database...")
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5
    )
    print("? Successfully connected to PostgreSQL")
    
    # Get PostgreSQL version
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"  Version: {version.split(',')[0]}")
    
    conn.close()
except psycopg2.OperationalError as e:
    print(f"? Connection failed: {e}")
    print("\nPossible solutions:")
    print("  1. Check PostgreSQL is running:")
    print("     Windows: Check Services for 'postgresql'")
    print("     Linux: sudo systemctl status postgresql")
    print("  2. Verify credentials in the script")
    print("  3. Check pg_hba.conf allows local connections")
    sys.exit(1)

# Test 2: Check for pgvector extension
print("\n[Test 2] Checking for pgvector extension...")
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5
    )
    
    with conn.cursor() as cur:
        # Check if extension is available
        cur.execute("""
            SELECT * FROM pg_available_extensions 
            WHERE name = 'vector';
        """)
        result = cur.fetchone()
        
        if result:
            print(f"? pgvector extension available")
            print(f"  Version: {result[1] if result[1] else 'Not installed'}")
        else:
            print("? pgvector extension not available")
            print("  Install pgvector:")
            print("  Windows: Download from https://github.com/pgvector/pgvector/releases")
            print("  Linux: sudo apt install postgresql-16-pgvector")
    
    conn.close()
except Exception as e:
    print(f"? Error checking pgvector: {e}")

# Test 3: Create test database
print("\n[Test 3] Testing database creation...")
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5
    )
    conn.autocommit = True
    
    with conn.cursor() as cur:
        # Try to create test database
        test_db = 'wherespace_test'
        
        # Drop if exists
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {};").format(
            sql.Identifier(test_db)
        ))
        
        # Create
        cur.execute(sql.SQL("CREATE DATABASE {};").format(
            sql.Identifier(test_db)
        ))
        print(f"? Created test database '{test_db}'")
        
        # Drop again
        cur.execute(sql.SQL("DROP DATABASE {};").format(
            sql.Identifier(test_db)
        ))
        print(f"? Dropped test database '{test_db}'")
    
    conn.close()
except Exception as e:
    print(f"? Error with database operations: {e}")

# Test 4: Test vectordb database
print("\n[Test 4] Checking vectordb database...")
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5
    )
    
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = 'vectordb';"
        )
        exists = cur.fetchone()
        
        if exists:
            print("? Database 'vectordb' exists")
            
            # Try to connect to it
            conn.close()
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                database='vectordb',
                user=PG_USER,
                password=PG_PASSWORD,
                connect_timeout=5
            )
            print("? Successfully connected to 'vectordb'")
            
            # Check for vector extension
            with conn.cursor() as cur2:
                cur2.execute("""
                    SELECT extname FROM pg_extension WHERE extname = 'vector';
                """)
                vector_ext = cur2.fetchone()
                
                if vector_ext:
                    print("? pgvector extension enabled in vectordb")
                else:
                    print("? pgvector extension not enabled in vectordb")
                    print("  It will be enabled automatically when needed")
        else:
            print("? Database 'vectordb' does not exist")
            print("  It will be created automatically when needed")
    
    conn.close()
except Exception as e:
    print(f"? Could not check vectordb: {e}")

# Test 5: Connection parameters
print("\n[Test 5] Testing connection parameters...")
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5
    )
    print("? Connection with keepalive parameters successful")
    
    # Get connection info
    info = conn.get_dsn_parameters()
    print(f"  Host: {info.get('host')}")
    print(f"  Port: {info.get('port')}")
    print(f"  Database: {info.get('dbname')}")
    print(f"  User: {info.get('user')}")
    
    conn.close()
except Exception as e:
    print(f"? Error with connection parameters: {e}")

# Summary
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("\nIf all tests passed, you're ready to run WhereSpace.py!")
print("\nIf there were errors:")
print("  1. Make sure PostgreSQL is running")
print("  2. Verify your credentials match the script")
print("  3. Check PostgreSQL logs for more details")
print("     Windows: Event Viewer ? Application logs")
print("     Linux: /var/log/postgresql/")
print("\n")
