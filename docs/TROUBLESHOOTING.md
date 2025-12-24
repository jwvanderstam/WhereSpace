# Troubleshooting Guide for Hanging Ingestion

## Problem: Program hangs during document ingestion

The PostgreSQL logs show "invalid length of startup packet" which indicates connection issues.

## Quick Diagnosis

### Step 1: Test PostgreSQL Connection
```bash
python simple_connection_test.py
```

This will test:
- Basic connection
- Multiple connections (detects keepalive issues)
- Connection to vectordb database

### Step 2: Check Ollama is Running
```bash
# Check if Ollama is responding
curl http://localhost:11434/api/tags

# Check Ollama logs (if running as service)
# The embedding generation might be timing out
```

### Step 3: Enable Debug Logging
Edit `WhereSpace.py` and change:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

Then run again to see exactly where it hangs.

## Common Causes

### 1. Ollama Not Responding
**Symptoms:** Hangs after "Generating embedding..."

**Solution:**
```bash
# Restart Ollama
ollama serve

# Or if using Docker
docker restart ollama
```

### 2. PostgreSQL Connection Issues
**Symptoms:** "invalid length of startup packet" in logs

**Fix Applied:** Removed keepalive parameters that cause issues with some PostgreSQL setups.

**Verify Fix:**
```bash
python simple_connection_test.py
```

### 3. Large Documents
**Symptoms:** Hangs on specific files

**Solution:** Already implemented - chunks are limited to 1000 chars

**Check:** Look for "Split X into Y chunks" messages

### 4. Database Lock
**Symptoms:** Hangs during database insert

**Solution:**
```sql
-- Connect to PostgreSQL
psql -U postgres -d vectordb

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Kill hanging queries
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' AND query LIKE '%documents%';
```

### 5. Network Issues (Docker)
**Symptoms:** Intermittent connection failures

**Solution:**
```bash
# Check Docker network
docker network inspect bridge

# Restart Docker containers
docker-compose restart
```

## Changes Made to Fix Issues

### 1. Removed Keepalive Parameters
**Before:**
```python
conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    keepalives=1,  # REMOVED
    keepalives_idle=30,  # REMOVED
    keepalives_interval=10,  # REMOVED
    keepalives_count=5  # REMOVED
)
```

**After:**
```python
conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    connect_timeout=10
)
```

### 2. Added Statement Timeout
```python
# Prevent queries from hanging forever
with conn.cursor() as cur:
    cur.execute("SET statement_timeout = '300000';")  # 5 minutes
```

### 3. Transaction Batching
```python
# Commit every 10 documents instead of every document
if i % 10 == 0:
    conn.commit()
```

### 4. Increased Embedding Timeout
```python
# From 30s to 60s
resp = requests.post(
    OLLAMA_EMBED_URL,
    json=payload,
    timeout=60  # Increased
)
```

### 5. Better Error Handling
```python
except Exception as e:
    logger.error(f"? Error processing {doc_path}: {e}")
    failed_count += 1
    try:
        conn.rollback()  # Clean rollback
    except:
        pass
    continue  # Keep processing other documents
```

## Monitoring Progress

### Watch Database Activity
```sql
-- In a separate terminal
psql -U postgres -d vectordb

-- Run this query repeatedly
SELECT 
    COUNT(*) as total_chunks,
    COUNT(DISTINCT file_path) as total_documents,
    MAX(created_at) as last_inserted
FROM documents;
```

### Watch Ollama
```bash
# Monitor Ollama resource usage
docker stats ollama  # If using Docker

# Or check system resources
top | grep ollama
```

### Enable Verbose Logging
In `WhereSpace.py`, change the log level to DEBUG:
```python
logger.setLevel(logging.DEBUG)
```

This will show:
- Each file being processed
- Chunk counts
- Embedding generation progress
- Database operations

## If Still Hanging

### 1. Test with Single Document
```python
# Modify main() temporarily
selected_docs = [documents_by_dir[selected_dir][0]]  # Just first doc
ingested = ingest_documents_to_pgvector(selected_docs)
```

### 2. Check Resource Usage
```bash
# CPU/Memory
htop  # Linux
Task Manager  # Windows

# Disk I/O
iotop  # Linux
```

### 3. Check Docker Logs
```bash
# PostgreSQL logs
docker logs postgres-container-name

# Ollama logs
docker logs ollama-container-name
```

### 4. Simplify Setup
Try without Docker:
- Install PostgreSQL locally
- Install Ollama locally
- Run `python WhereSpace.py`

## Expected Behavior

Normal ingestion should show:
```
?? Scanning C:\Users\...
? Completed! Scanned 45,321 files
?? Found 1,234 documents

?? Connecting to PostgreSQL...
? pgvector table initialized
?? Starting RAG ingestion for 110 documents...

? [1/110] Ingested: document1.txt (2 chunks)
? [2/110] Ingested: document2.pdf (5 chunks)
? [3/110] Ingested: document3.docx (3 chunks)
...

? RAG ingestion complete: 105 succeeded, 2 failed, 3 skipped
```

If it hangs, you'll see WHERE it stops.

## Contact/Report

If none of these solutions work, report the issue with:
1. Output of `simple_connection_test.py`
2. Last log message before hang
3. PostgreSQL logs
4. Ollama logs (if applicable)
5. System resources (CPU/Memory)
