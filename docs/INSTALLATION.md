# Installation Guide - JW zijn babbeldoos

## Quick Install (Automatic)

The application now automatically checks and installs missing dependencies!

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

The scripts will:
1. ? Check Python version (requires 3.8+)
2. ? Check pip availability
3. ? Upgrade pip to latest version
4. ? Check for missing dependencies
5. ? Automatically install missing packages
6. ? Start the application

---

## Manual Installation

If automatic installation fails, install dependencies manually:

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install flask
pip install requests
pip install psycopg2-binary
pip install pypdf
pip install python-docx
```

### 2. Install PostgreSQL with pgvector

**Windows:**
```bash
# Download and install PostgreSQL from:
# https://www.postgresql.org/download/windows/

# Enable pgvector extension
psql -U postgres -d postgres -c "CREATE EXTENSION vector;"
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-server-dev-all
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Enable extension
sudo -u postgres psql -c "CREATE EXTENSION vector;"
```

**Docker:**
```bash
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=Mutsmuts10 \
  -p 5432:5432 \
  ankane/pgvector
```

### 3. Install Ollama

**Windows/Mac/Linux:**

Download from: https://ollama.ai/download

Then pull required models:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text

# Optional additional models
ollama pull mistral
ollama pull gemma2
ollama pull qwen2.5
```

### 4. Verify Installation

Run the dependency checker:

```bash
python check_dependencies.py
```

Expected output:
```
======================================================================
CHECKING DEPENDENCIES
======================================================================

Checking installed packages...
  OK flask        - Web framework for chat interface
  OK requests     - HTTP library for Ollama communication
  OK psycopg2     - PostgreSQL database adapter
  OK pypdf        - PDF text extraction
  OK docx         - DOCX text extraction

======================================================================
All dependencies are installed!
======================================================================
```

---

## Troubleshooting

### Python not found
**Solution:** Install Python 3.8+ from https://www.python.org/downloads/

### pip not available
**Solution:** 
```bash
python -m ensurepip --upgrade
```

### psycopg2 installation fails
**Windows:** Use `psycopg2-binary` instead:
```bash
pip install psycopg2-binary
```

**Linux:** Install PostgreSQL development files:
```bash
sudo apt install libpq-dev python3-dev
pip install psycopg2
```

### pypdf installation fails
**Solution:** Try older version:
```bash
pip install pypdf==3.0.0
```

### Permission errors during installation
**Solution:** Use user installation:
```bash
pip install --user -r requirements.txt
```

Or use virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] pip available and upgraded
- [ ] All Python packages installed
- [ ] PostgreSQL installed and running
- [ ] pgvector extension enabled
- [ ] Ollama installed and running
- [ ] Required models pulled (llama3.1, nomic-embed-text)
- [ ] Can connect to PostgreSQL
- [ ] Can connect to Ollama

### Test PostgreSQL Connection
```bash
psql -U postgres -c "SELECT 1;"
```

### Test Ollama Connection
```bash
curl http://localhost:11434/api/tags
```

### Run Full Dependency Check
```bash
python check_dependencies.py
```

---

## Next Steps

Once all dependencies are installed:

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Or use quick start:**
   ```bash
   start.bat      # Windows
   ./start.sh     # Linux/Mac
   ```

3. **Follow the menu to:**
   - Analyze your storage
   - Ingest documents
   - Start web chat interface

---

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 10GB free disk space
- PostgreSQL 12+
- Ollama (any version)

### Recommended
- Python 3.10+
- 8GB RAM
- 20GB free disk space
- PostgreSQL 14+
- Ollama latest version

---

## Getting Help

If you encounter issues:

1. Check `TROUBLESHOOTING.md`
2. Run `python check_dependencies.py`
3. Check logs in console output
4. Verify PostgreSQL and Ollama are running

---

**Happy chatting with JW zijn babbeldoos! ??**
