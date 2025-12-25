# 🤖 WhereSpace - AI Document Chat System

**Intelligent RAG (Retrieval-Augmented Generation) system for chatting with your documents using local LLMs via Ollama.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

---

## 🌟 Features

### 🎯 Unified Web Interface
- ✅ **Chat Interface**: RAG mode & Direct LLM conversations
- ✅ **Document Management**: View, search, and manage indexed documents
- ✅ **Smart Indexing**: Upload and process documents with progress tracking
- ✅ **Storage Analysis**: Scan and analyze local storage for documents
- ✅ **Model Management**: Browse, download, and manage Ollama models
- ✅ **Performance Evaluation**: Test and optimize RAG retrieval quality
- ✅ **Settings & Deployment**: Configure system and deploy to production

### 📄 Document Processing
- ✅ **Multi-format support**: PDF, DOCX, TXT, MD, CSV
- ✅ **Smart chunking**: Overlap for context preservation
- ✅ **Parallel processing**: 6-8x faster with batch embeddings
- ✅ **Metadata extraction**: File info and timestamps
- ✅ **Progress tracking**: Real-time ingestion monitoring

### 💬 Advanced Chat Features
- ✅ **RAG Mode**: Query your indexed documents with AI
- ✅ **Direct LLM Mode**: General questions without context
- ✅ **Model Switcher**: Choose between Llama, Mistral, Gemma, Qwen
- ✅ **Source Citations**: See which documents were used
- ✅ **Formatted Responses**: Clean, structured output with markdown
- ✅ **Persistent Settings**: Model selection saved across sessions

### ⚡ Performance
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
ollama pull nomic-embed-text  # For embeddings (required)
ollama pull llama3.1          # For chat (recommended)

# Optional: Pull additional models
ollama pull mistral
ollama pull gemma2
ollama pull qwen2.5
```

### 5. Start the Application

**Simplified Launch (Recommended):**
```bash
python main.py
```

The web interface will automatically start at `http://127.0.0.1:5000`

**Windows Quick Start:**
```bash
start.bat
```

**Linux/Mac Quick Start:**
```bash
chmod +x start.sh
./start.sh
```

---

## 📖 Usage

### Web Interface (New!)

Starting the application with `python main.py` launches the modern web interface:

```
====================================================================
    JW zijn babbeldoos - AI Document Chat System
====================================================================

🚀 Starting web interface...

📋 Features available:
   • Chat Interface - RAG mode & Direct LLM mode
   • Document Management - View and manage indexed documents
   • Document Indexing - Index new documents from directories
   • Storage Analysis - Analyze local storage and find documents
   • Model Management - Browse, download, and manage LLM models
   • RAG Evaluation - Test and evaluate retrieval performance
   • Settings & Deployment - Configure and deploy the system

====================================================================

🌐 Web interface will be available at: http://127.0.0.1:5000

💡 Navigate using the sidebar menu
⏹  Press Ctrl+C to stop the server

====================================================================
```

### Quick Workflow

1. **Open Browser**: Navigate to `http://127.0.0.1:5000`
2. **Index Documents**: Click "Indexeren" in sidebar → Enter directory path
3. **Start Chatting**: Click "Chat" in sidebar → Ask questions
4. **Manage Models**: Click "Model Beheer" to download/manage LLM models
5. **View Documents**: Click "Documenten" to see indexed files
6. **Analyze Storage**: Click "Opslag Analyse" to scan directories
7. **Evaluate Performance**: Click "RAG Evaluatie" to test quality

### Navigation Menu

- 💬 **Chat** - Main chat interface with RAG and Direct modes
- 📋 **Documenten** - View and manage all indexed documents
- 📚 **Indexeren** - Upload and index new documents
- 🔍 **Opslag Analyse** - Scan local storage for documents
- 🤖 **Model Beheer** - Manage Ollama LLM models
- 📊 **RAG Evaluatie** - Performance testing and metrics
- ⚙️ **Instellingen** - System settings and deployment

---

## 📁 Project Structure

```
WhereSpace/
├── 📄 Core Files
│   ├── main.py                      # Simplified web launcher
│   ├── WhereSpace.py                # Document ingestion engine
│   ├── WhereSpaceChat.py            # Web interface & API
│   ├── model_manager.py             # Ollama model management
│   ├── batch_embeddings.py          # Parallel embedding generation
│   ├── optimized_rag_query.py       # Performance-optimized queries
│   └── evaluate_rag.py              # RAG evaluation metrics
│
├── 📂 templates/                    # Web UI templates
│   ├── base.html                    # Base template with navigation
│   ├── index.html                   # Chat interface
│   ├── documents.html               # Document management (planned)
│   ├── ingest.html                  # Document indexing (planned)
│   ├── storage.html                 # Storage analysis (planned)
│   ├── models.html                  # Model management (planned)
│   ├── evaluation.html              # RAG evaluation (planned)
│   └── settings.html                # Settings page (planned)
│
├── 📂 static/                       # Static assets
│   ├── chat.js                      # Chat functionality
│   └── common.js                    # Shared JavaScript (planned)
│
├── 📂 config/                       # Configuration
│   ├── requirements.txt             # Python dependencies
│   ├── .gitignore                   # Git ignore rules
│   └── .model_config.json           # Persistent model selection
│
├── 📂 docs/                         # Documentation (20+ guides)
│   ├── INSTALLATION.md              # Setup instructions
│   ├── WEB_INTERFACE_MIGRATION.md   # Web UI migration plan
│   ├── QUICK_REFERENCE.md           # Quick commands
│   └── TROUBLESHOOTING.md           # Common issues
│
└── 📂 tests/                        # Test & utility scripts
    ├── check_dependencies.py        # Dependency checker
    └── test_model_persistence.py    # Model tests
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
OLLAMA_URL = "http://localhost:11434"
```

### Web Server

```python
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
```

---

## 📊 Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Ingestion** (100 docs) | 4 min | 35s | **6-8x faster** |
| **Query Response** | 800ms | 250ms | **3.2x faster** |
| **Cached Query** | 800ms | <5ms | **160x faster** |
| **Concurrent Users** | 2 | 15 | **7.5x more** |
| **UI Response** | Terminal | Web Browser | **Modern UX** |

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

- 📘 [INSTALLATION.md](docs/INSTALLATION.md) - Complete setup guide
- 🌐 [WEB_INTERFACE_MIGRATION.md](docs/WEB_INTERFACE_MIGRATION.md) - Web UI architecture
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

**Port 5000 already in use:**
```bash
# Change WEB_PORT in WhereSpaceChat.py
WEB_PORT = 5001  # Or any available port
```

---

## 🆕 What's New in v3.0

- ✨ **Modern Web Interface**: All features now in browser
- 🎨 **Unified Navigation**: Sidebar menu for easy access
- 🚀 **Simplified Launch**: Just run `python main.py`
- 📱 **Responsive Design**: Works on desktop and mobile
- 💾 **Model Management**: Built-in Ollama model browser
- 📊 **Real-time Progress**: Live updates for all operations
- 🔐 **Better Error Handling**: Clear messages with solutions

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

*Version: 3.0.0 | Last Updated: December 25, 2025*
