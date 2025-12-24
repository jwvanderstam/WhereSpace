# -*- coding: utf-8 -*-
"""
Simple PostgreSQL Connection Test
==================================

Minimal test to diagnose connection issues.
"""

import sys

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)

# Configuration
PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"

print("Testing PostgreSQL connection...")
print(f"Host: {PG_HOST}")
print(f"Port: {PG_PORT}")
print(f"User: {PG_USER}")
print()

# Test 1: Simple connection
print("[1] Testing basic connection to 'postgres' database...")
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5
    )
    print("? Connection successful!")
    
    # Test query
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"? PostgreSQL version: {version.split(',')[0]}")
    
    conn.close()
    print("? Connection closed cleanly")
    
except psycopg2.OperationalError as e:
    print(f"? Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Is PostgreSQL running?")
    print("   Docker: docker ps | grep postgres")
    print("   Windows: services.msc ? postgresql")
    print("   Linux: sudo systemctl status postgresql")
    print()
    print("2. Check credentials match your PostgreSQL setup")
    print("3. Check firewall allows port 5432")
    sys.exit(1)
except Exception as e:
    print(f"? Unexpected error: {e}")
    sys.exit(1)

# Test 2: Multiple connections
print("\n[2] Testing multiple connections (detecting keepalive issues)...")
try:
    connections = []
    for i in range(3):
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database='postgres',
            user=PG_USER,
            password=PG_PASSWORD,
            connect_timeout=5
        )
        connections.append(conn)
        print(f"? Connection {i+1} established")
    
    # Close all
    for i, conn in enumerate(connections):
        conn.close()
        print(f"? Connection {i+1} closed")
    
    print("? Multiple connections work correctly")
    
except Exception as e:
    print(f"? Multiple connection test failed: {e}")
    # Clean up
    for conn in connections:
        try:
            conn.close()
        except:
            pass

# Test 3: vectordb database
print("\n[3] Testing connection to 'vectordb' database...")
try:
    # First check if it exists
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        connect_timeout=5
    )
    
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'vectordb';")
        exists = cur.fetchone()
    
    conn.close()
    
    if exists:
        print("? Database 'vectordb' exists")
        
        # Try to connect to it
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database='vectordb',
            user=PG_USER,
            password=PG_PASSWORD,
            connect_timeout=5
        )
        print("? Successfully connected to 'vectordb'")
        conn.close()
    else:
        print("? Database 'vectordb' does not exist (will be created automatically)")
        
except Exception as e:
    print(f"? Error testing vectordb: {e}")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
print("\nIf all tests passed, the PostgreSQL connection is working.")
print("If ingestion still hangs, the issue is likely with:")
print("  - Ollama embedding generation (check ollama logs)")
print("  - Large documents taking too long to process")
print("  - Network connectivity between services")
print()
