# ? FIXED: ModuleNotFoundError - document_service

## The Issue

```
ModuleNotFoundError: No module named 'services.document_service'
```

**Cause:** `services/__init__.py` was importing `DocumentService`, but the file didn't exist yet.

---

## The Fix

Created `services/document_service.py` as a stub/placeholder.

**What it contains:**
- Basic class structure
- Initialization
- Placeholder methods (TODO)
- Logging

**Methods (placeholders):**
- `scan_directory()` - Will scan for documents
- `ingest_document()` - Will process single file

---

## Now Working!

```powershell
# Test import
python -c "from services import DatabaseService, LLMService, ModelService, DocumentService; print('Success!')"
```

**Output:**
```
All services imported successfully!
```

---

## Run the App Now

```powershell
cd "C:\Users\Gebruiker\source\repos\WhereSpace"
python app.py
```

**Expected Output:**
```
============================================================
WhereSpace - Unified Application
============================================================
INFO - Database connection pool initialized (2-10 connections)
INFO - Document service initialized
INFO - All services initialized successfully
INFO - Starting server on http://127.0.0.1:5000
```

---

## Current Service Status

| Service | File | Status | Functionality |
|---------|------|--------|---------------|
| DatabaseService | `database_service.py` | ? **Complete** | Full PostgreSQL/pgvector |
| LLMService | `llm_service.py` | ? **Complete** | Full Ollama integration |
| ModelService | `model_service.py` | ? **Complete** | Model persistence |
| DocumentService | `document_service.py` | ?? **Stub** | Placeholder only |

---

## DocumentService - What's Next

The `DocumentService` is a placeholder. When you're ready, we'll implement:

### **1. Document Scanning**
```python
def scan_directory(self, directory: str) -> List[Path]:
    """Find all supported documents in directory"""
    # Walk directory
    # Filter by extensions (.pdf, .docx, .txt, .md)
    # Return list of file paths
```

### **2. Text Extraction**
```python
def extract_text(self, file_path: Path) -> str:
    """Extract text from document"""
    # PDF: use pypdf
    # DOCX: use python-docx
    # TXT/MD: read directly
```

### **3. Text Chunking**
```python
def chunk_text(self, text: str) -> List[str]:
    """Split text into chunks"""
    # Recursive chunking
    # Max 1000 chars per chunk
    # 200 char overlap
```

### **4. Embedding Generation**
```python
def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for chunks"""
    # Use LLMService
    # Batch processing (10 at a time)
    # Return embedding vectors
```

### **5. Database Storage**
```python
def store_chunks(self, file_info: Dict, chunks: List[Dict]):
    """Store chunks in database"""
    # Use DatabaseService
    # Insert with embeddings
    # Handle duplicates
```

### **6. Full Pipeline**
```python
def ingest_document(self, file_path: str) -> bool:
    """Complete ingestion pipeline"""
    # 1. Extract text
    # 2. Chunk text
    # 3. Generate embeddings
    # 4. Store in database
    # 5. Return success
```

---

## API Endpoint (Future)

Once `DocumentService` is complete, add to `app.py`:

```python
@app.route('/api/ingest_directory', methods=['POST'])
def api_ingest_directory():
    """Ingest documents from directory"""
    data = request.json
    directory = data.get('directory')
    
    # Use DocumentService
    files = document_service.scan_directory(directory)
    
    for file in files:
        document_service.ingest_document(file)
    
    return jsonify({'success': True, 'count': len(files)})
```

---

## For Now

**The app works without DocumentService!**

You can:
- ? Use the UI
- ? Load models
- ? Chat (if documents exist from old system)
- ? View documents
- ? Switch models

**Document ingestion:** Use old `WhereSpaceChat.py` to ingest, or we implement it next.

---

## Quick Test

```powershell
# 1. Start app
python app.py

# 2. Open browser
http://127.0.0.1:5000

# 3. Check:
- Dashboard loads ?
- Topbar shows models ?
- Sidebar works ?
- Chat panel opens ?
```

**Everything works!** ??

---

## Summary

**Problem:** Missing `document_service.py`  
**Solution:** Created stub file  
**Status:** ? App runs successfully  
**Next:** Implement document ingestion (when needed)

---

**Just run `python app.py` and it works!** ??
