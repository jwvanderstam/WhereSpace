# 🤖 WhereSpace - AI Document Chat System

**Intelligent RAG (Retrieval-Augmented Generation) system for chatting with your documents using local LLMs via Ollama.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

---

## 🌟 Features

### Document Processing
- ✅ **Multi-format support**: PDF, DOCX, TXT, MD, CSV
- ✅ **Smart chunking**: Overlap for context preservation
- ✅ **Parallel processing**: 6-8x faster with batch embeddings
- ✅ **Metadata extraction**: File info and timestamps
- ✅ **Progress tracking**: Real-time ingestion monitoring

### Web Chat Interface
- ✅ **RAG Mode**: Query your indexed documents with AI
- ✅ **Direct LLM Mode**: General questions without context
- ✅ **Model Switcher**: Choose between Llama, Mistral, Gemma, Qwen
- ✅ **Source Citations**: See which documents were used
- ✅ **Formatted Responses**: Clean, structured output with markdown
- ✅ **Persistent Settings**: Model selection saved across sessions

### Performance
- ✅ **Connection Pooling**: 25-40% faster queries
- ✅ **Query Caching**: <1ms for repeated queries
- ✅ **Parallel Embeddings**: 6-8x faster ingestion
- ✅ **Optimized Indexes**: pgvector IVFFlat/HNSW

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **PostgreSQL**: 14+ with pgvector extension
- **Ollama**: Latest version with embedding model
- **OS**: Windows, Linux, or macOS

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jwvanderstam/WhereSpace.git
cd WhereSpace
```

### 2. Install Dependencies

```bash
pip install -r config/requirements.txt
```

The application will automatically check and install missing dependencies on first run.

### 3. Setup PostgreSQL

```sql
-- Create database
CREATE DATABASE vectordb;

-- Enable pgvector extension
\c vectordb
CREATE EXTENSION vector;
```

### 4. Setup Ollama

```bash
# Install Ollama (https://ollama.ai)

# Pull required models
ollama pull nomic-embed-text  # For embeddings
ollama pull llama3.1          # For chat (default)

# Optional: Pull additional models
ollama pull mistral
ollama pull gemma2
ollama pull qwen2.5
```

### 5. Run the Application

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Python:**
```bash
python main.py
```

---

## 📖 Usage

### Main Menu

When you run `python main.py`, you'll see:

```
============================================================
    JW zijn babbeldoos - AI Document Chat System
============================================================

HOOFDMENU
============================================================

1. 🔍 Analyseer lokale opslag
   - Scan directories voor bestanden
   - Bekijk storage verdeling
   - Identificeer documenten voor indexering

2. 📚 Indexeer documenten
   - Selecteer directory met documenten
   - Extract en chunk tekst
   - Genereer embeddings en sla op

3. 💬 Start web chat interface
   - RAG mode: Query geindexeerde documenten
   - Direct LLM mode: Algemene vragen
   - Model switcher (Llama, Mistral, Gemma, Qwen)

4. 📊 Evalueer RAG performance
   - Test retrieval kwaliteit
   - Bekijk Hit Rate en MRR metrics

5. 📋 Bekijk geindexeerde documenten
   - Toon alle documenten in database
   - Bekijk chunk counts en details

0. 🚪 Afsluiten
```

### Quick Workflow

1. **First time**: Choose option **1** to analyze your storage
2. **Index documents**: Choose option **2** and select a directory
3. **Start chatting**: Choose option **3** to launch web interface at `http://127.0.0.1:5000`
4. **Evaluate**: Choose option **4** to test retrieval quality

### Web Interface Only

To start only the web chat interface:

```bash
python WhereSpaceChat.py
# Navigate to: http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
WhereSpace/
├── 📄 Core Files (6 Python files)
│   ├── main.py                      # Main menu application
│   ├── WhereSpace.py                # Document ingestion engine
│   ├── WhereSpaceChat.py            # Web chat interface
│   ├── batch_embeddings.py          # Parallel embedding generation
│   ├── optimized_rag_query.py       # Performance-optimized queries
│   └── evaluate_rag.py              # RAG evaluation metrics
│
├── 📂 templates/                    # Web UI templates
│   └── index.html                   # Chat interface
│
├── 📂 config/                       # Configuration files
│   ├── requirements.txt             # Python dependencies
│   ├── .gitignore                   # Git ignore rules
│   └── .model_config.json           # Persistent model selection
│
├── 📂 docs/                         # Documentation (20+ guides)
│   ├── INSTALLATION.md              # Setup instructions
│   ├── QUICK_REFERENCE.md           # Quick commands
│   ├── TROUBLESHOOTING.md           # Common issues
│   └── ... (17 more guides)
│
├── 📂 tests/                        # Test & utility scripts
│   ├── check_dependencies.py        # Dependency checker
│   ├── test_model_persistence.py    # Model tests
│   └── ... (5 more utilities)
│
└── 📂 scripts/                      # Utility scripts
    ├── start.bat                    # Windows launcher
    └── start.sh                     # Linux/Mac launcher
```

---

## ⚙️ Configuration

### Database Settings

Edit `WhereSpace.py` and `WhereSpaceChat.py`:

```python
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "vectordb"
PG_USER = "postgres"
PG_PASSWORD = "your_password"
```

### Ollama Settings

```python
OLLAMA_EMBED_MODEL = "nomic-embed-text"
```

---

## 📊 Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Ingestion** (100 docs) | 4 min | 35s | **6-8x faster** |
| **Query Response** | 800ms | 250ms | **3.2x faster** |
| **Cached Query** | 800ms | <5ms | **160x faster** |
| **Concurrent Users** | 2 | 15 | **7.5x more** |

---

## 🧪 Testing

```bash
# Check dependencies
python tests/check_dependencies.py

# Test database connection
python tests/test_postgres_connection.py

# Test model persistence
python tests/test_model_persistence.py
```

---

## 📚 Documentation

All documentation is in the `docs/` directory (20+ guides):

- 📘 [INSTALLATION.md](docs/INSTALLATION.md) - Complete setup
- ⚡ [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Quick commands
- 🔧 [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- 📊 [COMPREHENSIVE_OPTIMIZATION_GUIDE.md](docs/COMPREHENSIVE_OPTIMIZATION_GUIDE.md) - Performance tuning

---

## 🔧 Troubleshooting

### Common Issues

**Module not found:**
```bash
pip install -r config/requirements.txt
```

**PostgreSQL connection failed:**
```bash
python tests/test_postgres_connection.py
```

**Ollama not responding:**
```bash
ollama serve
ollama list
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 👥 Author

**JW van der Stam**
- GitHub: [@jwvanderstam](https://github.com/jwvanderstam)

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM infrastructure
- **pgvector** - Vector similarity search
- **PostgreSQL** - Database engine
- **Flask** - Web framework

---

**Made with ❤️ for document intelligence**

*Version: 2.0.0 | Last Updated: December 24, 2025*
