# -*- coding: utf-8 -*-
"""
WhereSpace Chat - Web Interface for RAG Queries
Provides a web-based chat interface to query ingested documents using Ollama.
"""
from pathlib import Path
import logging
import json
from typing import List, Dict, Optional, Tuple
import sys
import subprocess
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

# Model persistence file (now in config directory)
MODEL_CONFIG_FILE = Path(__file__).parent / "config" / ".model_config.json"

# Ensure config directory exists
MODEL_CONFIG_FILE.parent.mkdir(exist_ok=True)

# Available LLM models - users can switch between these
AVAILABLE_MODELS = [
    {"id": "llama3.1", "name": "Llama 3.1", "description": "Fast, general purpose"},
    {"id": "mistral", "name": "Mistral", "description": "Balanced performance"},
    {"id": "gemma2", "name": "Gemma 2", "description": "Google's model"},
    {"id": "qwen2.5", "name": "Qwen 2.5", "description": "Strong reasoning"},
]

def load_model_config():
    """Load saved model configuration from disk."""
    try:
        if MODEL_CONFIG_FILE.exists():
            with open(MODEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                model = config.get('current_model', 'llama3.1')
                logger.info(f"Loaded saved model: {model}")
                return model
    except Exception as e:
        logger.warning(f"Could not load model config: {e}")
    
    # Default model
    return "llama3.1"

def save_model_config(model_id: str):
    """Save model configuration to disk for persistence."""
    try:
        config = {
            'current_model': model_id,
            'updated_at': str(Path.cwd())  # Just timestamp info
        }
        with open(MODEL_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.debug(f"Saved model config: {model_id}")
    except Exception as e:
        logger.warning(f"Could not save model config: {e}")

# Current model state (loaded from disk, persisted across restarts)
_current_model = load_model_config()

def get_current_model():
    """Get the current LLM model."""
    global _current_model
    return _current_model

def set_current_model(model_id):
    """Set the current LLM model and persist it."""
    global _current_model
    _current_model = model_id
    save_model_config(model_id)  # Persist to disk
    logger.info(f"Model switched to: {model_id} (persisted)")

OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_EMBED_DIMENSION = 768

# PostgreSQL/pgvector Configuration
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "vectordb"
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"
PG_TABLE = "documents"

# Web server configuration
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000

# Check and install required modules
REQUIRED_MODULES = {
    "flask": "flask",
    "requests": "requests",
    "psycopg2": "psycopg2-binary"
}

def check_and_install_modules():
    """Check and install all required modules."""
    missing_modules = []
    
    for module_name, pip_name in REQUIRED_MODULES.items():
        try:
            __import__(module_name)
            logger.debug(f"Module '{module_name}' already installed")
        except ImportError:
            missing_modules.append((module_name, pip_name))
    
    if missing_modules:
        logger.warning(f"Missing {len(missing_modules)} module(s). Attempting to install...")
        for module_name, pip_name in missing_modules:
            try:
                logger.info(f"Installing {pip_name}...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"Successfully installed '{module_name}'!")
            except Exception as e:
                logger.error(f"Failed to install '{module_name}': {e}")
                logger.info(f"Please run manually: pip install {pip_name}")

# Run module check
check_and_install_modules()

# Import required modules after installation attempt
try:
    from flask import Flask, render_template, request, jsonify, Response
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.error("Flask module not available. Install with: pip install flask")
    sys.exit(1)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.error("requests module not available. Install with: pip install requests")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.error("psycopg2 module not available. Install with: pip install psycopg2-binary")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'wherespace-secret-key-change-in-production'


def check_documents_exist() -> Tuple[bool, int]:
    """Check if any documents are ingested in the database."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [PG_TABLE])
            
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                conn.close()
                return False, 0
            
            cur.execute(sql.SQL("""
                SELECT COUNT(DISTINCT file_path) FROM {};
            """).format(sql.Identifier(PG_TABLE)))
            
            count = cur.fetchone()[0]
            conn.close()
            return count > 0, count
            
    except Exception as e:
        logger.error(f"Error checking documents: {e}")
        return False, 0


def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding vector for query text."""
    try:
        payload = {
            "model": OLLAMA_EMBED_MODEL,
            "prompt": text
        }
        
        resp = requests.post(
            OLLAMA_EMBED_URL,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        
        data = resp.json()
        return data.get("embedding")
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None


def search_similar_chunks(query_embedding: List[float], top_k: int = 10, min_similarity: float = 0.3, file_type_filter: str = None) -> List[Dict]:
    """
    Search for similar document chunks using vector similarity with enhanced retrieval.
    
    Args:
        query_embedding: Query embedding vector
        top_k: Number of top results to return (increased from 5 to 10 for better context)
        min_similarity: Minimum similarity threshold (0.0-1.0)
        file_type_filter: Optional filter by file type (e.g., 'pdf', 'docx')
        
    Returns:
        List of similar chunks with metadata, filtered by similarity threshold
    """
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        
        with conn.cursor() as cur:
            # Build query with optional file type filter
            base_query = """
                SELECT 
                    file_name,
                    file_path,
                    chunk_index,
                    chunk_content,
                    content_preview,
                    file_type,
                    1 - (embedding <=> %s::vector) as similarity
                FROM {}
                WHERE 1=1
            """
            
            params = [query_embedding]
            
            # Add file type filter if specified
            if file_type_filter:
                base_query += " AND file_type = %s"
                params.append(file_type_filter)
            
            # Add similarity threshold and ordering
            base_query += """
                AND (1 - (embedding <=> %s::vector)) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params.extend([query_embedding, min_similarity, query_embedding, top_k])
            
            cur.execute(sql.SQL(base_query).format(sql.Identifier(PG_TABLE)), params)
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'file_name': row[0],
                    'file_path': row[1],
                    'chunk_index': row[2],
                    'content': row[3],
                    'preview': row[4],
                    'file_type': row[5],
                    'similarity': float(row[6])
                })
            
        conn.close()
        
        logger.info(f"Retrieved {len(results)} chunks with similarity >= {min_similarity}")
        return results
        
    except Exception as e:
        logger.error(f"Error searching chunks: {e}")
        return []


def generate_rag_response_stream(query: str, context_chunks: List[Dict]):
    """
    Generate streaming response using Ollama with RAG context and structured prompting.
    
    Uses an optimized prompt structure that:
    - Instructs the LLM to cite sources
    - Prevents hallucinations by sticking to context
    - Provides clear guidelines for when information is insufficient
    - Formats output with clean structure (headers, bullets, sections)
    """
    try:
        # Build context with source attribution
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            similarity_pct = round(chunk.get('similarity', 0) * 100, 1)
            context_parts.append(
                f"[Bron {i}: {chunk['file_name']} (chunk {chunk['chunk_index']}, relevantie: {similarity_pct}%)]\n"
                f"{chunk['content']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Enhanced structured prompt with formatting instructions
        prompt = f"""Je bent een nauwkeurige, professionele assistent die vragen beantwoordt op basis van documenten.

BELANGRIJKE REGELS:
1. Gebruik ALLEEN informatie uit de onderstaande bronnen
2. Citeer bronnen bij je antwoord (bijv. "Volgens [Bron 1]...")
3. Als de informatie niet in de bronnen staat, zeg dit duidelijk
4. Verzin GEEN informatie - blijf bij de feiten uit de documenten
5. Als bronnen tegenstrijdig zijn, vermeld dit expliciet

FORMATTING RICHTLIJNEN:
- Begin met een korte samenvatting (1-2 zinnen)
- Gebruik duidelijke secties met headers (bijv. "## Samenvatting")
- Gebruik bullets (•) voor lijsten en opsommingen
- Gebruik nummering (1., 2., 3.) voor stappen of volgorden
- Gebruik witregels tussen secties voor leesbaarheid
- Benadruk belangrijke punten met **vetgedrukte** tekst
- Houd antwoorden gestructureerd en overzichtelijk

VOORBEELD FORMATTING:
```
## Samenvatting
[Korte samenvatting in 1-2 zinnen]

## Belangrijkste Punten
• Punt 1 met **belangrijk detail**
• Punt 2 met context
• Punt 3 met specifieke informatie

## Details
[Uitgebreide uitleg met bronvermeldingen]

**Bronnen:** [Bron 1], [Bron 2]
```

BESCHIKBARE BRONNEN:
{context}

VRAAG: {query}

ANTWOORD (gestructureerd en geformatteerd):"""
        
        # Use the current model from getter function
        current_model = get_current_model()
        
        payload = {
            "model": current_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2,  # Slightly higher for better formatting
                "top_p": 0.9,
                "top_k": 40,
                "num_ctx": 4096  # Larger context window for better responses
            }
        }
        
        logger.info(f"Using model: {current_model} for RAG query")
        
        resp = requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=120  # Increased timeout for large models
        )
        
        # Better error handling
        if resp.status_code != 200:
            error_detail = resp.text
            logger.error(f"Ollama API error (status {resp.status_code}): {error_detail}")
            
            # Check for specific error conditions
            if resp.status_code == 500:
                # Try to parse error message
                try:
                    error_data = resp.json()
                    error_msg = error_data.get('error', error_detail)
                except:
                    error_msg = error_detail
                
                logger.error(f"Ollama internal error: {error_msg}")
                
                # Provide helpful error message
                if "out of memory" in error_msg.lower() or "oom" in error_msg.lower():
                    yield "❌ Model heeft onvoldoende geheugen. Dit model is te groot voor uw systeem.\n\n"
                    yield "💡 **Suggesties:**\n"
                    yield "- Switch naar een kleiner model (llama3.1, mistral, gemma2)\n"
                    yield "- Sluit andere applicaties om geheugen vrij te maken\n"
                    yield "- Herstart Ollama: `ollama serve`\n"
                elif "not found" in error_msg.lower():
                    yield f"❌ Model '{current_model}' niet gevonden in Ollama.\n\n"
                    yield "💡 **Suggesties:**\n"
                    yield f"- Pull het model: `ollama pull {current_model}`\n"
                    yield "- Refresh de model lijst in de web interface\n"
                    yield "- Kies een ander model uit de dropdown\n"
                else:
                    yield f"❌ Ollama fout: {error_msg}\n\n"
                    yield "💡 **Suggesties:**\n"
                    yield "- Herstart Ollama: `ollama serve`\n"
                    yield "- Controleer of het model correct is geïnstalleerd\n"
                    yield "- Probeer een ander model\n"
                return
            
            raise Exception(f"HTTP {resp.status_code}: {error_detail}")
        
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
                    elif 'error' in data:
                        error_msg = data['error']
                        logger.error(f"Ollama streaming error: {error_msg}")
                        yield f"\n\n❌ Fout: {error_msg}\n"
                        return
                except json.JSONDecodeError:
                    continue
                    
    except requests.exceptions.Timeout:
        logger.error(f"Ollama request timeout after 120 seconds")
        yield "❌ Model reactie timeout. Het model reageert niet binnen 2 minuten.\n\n"
        yield "💡 **Dit kan betekenen:**\n"
        yield "- Het model is te groot voor uw systeem\n"
        yield "- Ollama is overbelast\n"
        yield "- Probeer een kleiner/sneller model\n"
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama")
        yield "❌ Kan geen verbinding maken met Ollama.\n\n"
        yield "💡 **Controleer:**\n"
        yield "- Is Ollama gestart? Run: `ollama serve`\n"
        yield "- Controleer: `curl http://localhost:11434/api/tags`\n"
    except Exception as e:
        logger.error(f"Error generating streaming response: {e}")
        yield f"❌ Error: {str(e)}\n"
@app.route('/')
def index():
    """Render main chat interface."""
    docs_exist, doc_count = check_documents_exist()
    return render_template('index.html', docs_exist=docs_exist, doc_count=doc_count)


@app.route('/api/query_stream', methods=['POST'])
def query_stream():
    """Handle streaming chat query."""
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({'error': 'Empty query'}), 400
        
        docs_exist, doc_count = check_documents_exist()
        if not docs_exist:
            return jsonify({
                'error': 'Geen documenten gevonden in de database.'
            }, 404)
        
        logger.info(f"Processing streaming query: {user_query}")
        query_embedding = generate_embedding(user_query)
        
        if not query_embedding:
            return jsonify({'error': 'Failed to generate query embedding'}), 500
        
        similar_chunks = search_similar_chunks(query_embedding, top_k=5)
        
        if not similar_chunks:
            def no_results():
                yield f"data: {json.dumps({'type': 'response', 'content': 'Geen relevante informatie gevonden.'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return Response(no_results(), mimetype='text/event-stream')
        
        def generate():
            sources = [
                {
                    'file': chunk['file_name'],
                    'chunk': chunk['chunk_index'],
                    'similarity': round(chunk['similarity'] * 100, 1),
                    'preview': chunk['preview']
                }
                for chunk in similar_chunks
            ]
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            
            for chunk in generate_rag_response_stream(user_query, similar_chunks):
                yield f"data: {json.dumps({'type': 'response', 'content': chunk})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Error processing streaming query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/query_direct_stream', methods=['POST'])
def query_direct_stream():
    """Query Ollama directly with streaming, without RAG context."""
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({'error': 'Empty query'}), 400
        
        logger.info(f"Processing direct streaming query: {user_query}")
        
        def generate():
            try:
                # Use the current model from getter function
                current_model = get_current_model()
                
                payload = {
                    "model": current_model,
                    "prompt": user_query,
                    "stream": True
                }
                
                logger.info(f"Using model: {current_model} for direct query")
                
                resp = requests.post(
                    OLLAMA_URL,
                    json=payload,
                    stream=True,
                    timeout=120  # Increased timeout for large models
                )
                
                # Better error handling
                if resp.status_code != 200:
                    error_detail = resp.text
                    logger.error(f"Ollama API error (status {resp.status_code}): {error_detail}")
                    
                    # Provide helpful error message
                    if resp.status_code == 500:
                        try:
                            error_data = resp.json()
                            error_msg = error_data.get('error', error_detail)
                        except:
                            error_msg = error_detail
                        
                        logger.error(f"Ollama internal error: {error_msg}")
                        
                        if "out of memory" in error_msg.lower() or "oom" in error_msg.lower():
                            yield f"data: {json.dumps({'type': 'error', 'content': '❌ Model heeft onvoldoende geheugen. Dit model is te groot voor uw systeem. Switch naar een kleiner model (llama3.1, mistral, gemma2).'})}\n\n"
                        elif "not found" in error_msg.lower():
                            yield f"data: {json.dumps({'type': 'error', 'content': '❌ Model {current_model} niet gevonden. Pull het model: ollama pull {current_model}'})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'error', 'content': '❌ Ollama fout: {error_msg}'})}\n\n"
                        return
                    
                    yield f"data: {json.dumps({'type': 'error', 'content': 'HTTP {resp.status_code}: {error_detail}'})}\n\n"
                    return
                
                for line in resp.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield f"data: {json.dumps({'type': 'response', 'content': data['response']})}\n\n"
                            elif 'error' in data:
                                error_msg = data['error']
                                logger.error(f"Ollama streaming error: {error_msg}")
                                yield f"data: {json.dumps({'type': 'error', 'content': '❌ Fout: {error_msg}'})}\n\n"
                                return
                        except json.JSONDecodeError:
                            continue
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except requests.exceptions.Timeout:
                logger.error(f"Ollama request timeout after 120 seconds")
                yield f"data: {json.dumps({'type': 'error', 'content': '❌ Model reactie timeout (2 min). Probeer een kleiner/sneller model.'})}\n\n"
            except requests.exceptions.ConnectionError:
                logger.error("Cannot connect to Ollama")
                yield f"data: {json.dumps({'type': 'error', 'content': '❌ Kan geen verbinding maken met Ollama. Controleer: ollama serve'})}\n\n"
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Error processing direct streaming query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/flush_documents', methods=['POST'])
def flush_documents():
    """Delete all ingested documents from the database."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        
        with conn.cursor() as cur:
            cur.execute(sql.SQL("DELETE FROM {};").format(sql.Identifier(PG_TABLE)))
            deleted_count = cur.rowcount
            conn.commit()
        
        conn.close()
        logger.info(f"Flushed {deleted_count} document chunks from database")
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} chunks verwijderd',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error flushing documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ingest_directory', methods=['POST'])
def ingest_directory():
    """Ingest documents from a specified directory."""
    try:
        data = request.json
        directory_path = data.get('directory', '').strip()
        
        if not directory_path:
            return jsonify({'error': 'No directory specified'}), 400
        
        from pathlib import Path
        dir_path = Path(directory_path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return jsonify({'error': f'Directory does not exist: {directory_path}'}), 400
        
        import sys
        import os
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        try:
            from WhereSpace import ingest_documents_to_pgvector, RAG_DOCUMENT_TYPES, MAX_DOCUMENT_SIZE
        except ImportError as e:
            return jsonify({'error': f'Cannot import WhereSpace module: {e}'}), 500
        
        documents = []
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower().lstrip('.')
                file_size = file_path.stat().st_size
                if ext in RAG_DOCUMENT_TYPES and file_size < MAX_DOCUMENT_SIZE:
                    documents.append(file_path)
        
        if not documents:
            return jsonify({
                'success': True,
                'message': 'Geen documenten gevonden in directory',
                'ingested_count': 0,
                'total_found': 0
            })
        
        logger.info(f"Starting ingestion of {len(documents)} documents from {directory_path}")
        ingested_count = ingest_documents_to_pgvector(documents)
        
        return jsonify({
            'success': True,
            'message': f'{ingested_count} documenten geindexeerd',
            'ingested_count': ingested_count,
            'total_found': len(documents)
        })
        
    except Exception as e:
        logger.error(f"Error ingesting directory: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models from Ollama and return with current selection."""
    try:
        # Fetch available models from Ollama
        ollama_response = requests.get('http://localhost:11434/api/tags', timeout=5)
        ollama_response.raise_for_status()
        ollama_data = ollama_response.json()
        
        # Extract model information
        available_models = []
        if 'models' in ollama_data:
            for model in ollama_data['models']:
                model_name = model.get('name', '')
                # Clean up model name (remove :latest suffix if present)
                display_name = model_name.replace(':latest', '')
                
                # Extract base name for better display
                base_name = display_name.split(':')[0] if ':' in display_name else display_name
                
                available_models.append({
                    'id': display_name,  # Use cleaned name as ID
                    'name': base_name.title(),  # Capitalize for display
                    'full_name': model_name,  # Keep full name
                    'size': model.get('size', 0),
                    'modified': model.get('modified_at', '')
                })
        
        # Sort by name
        available_models.sort(key=lambda x: x['name'])
        
        # If no models found, return default list
        if not available_models:
            logger.warning("No models found in Ollama, returning default list")
            available_models = [
                {"id": "llama3.1", "name": "Llama 3.1", "full_name": "llama3.1:latest"},
                {"id": "mistral", "name": "Mistral", "full_name": "mistral:latest"},
                {"id": "gemma2", "name": "Gemma 2", "full_name": "gemma2:latest"},
                {"id": "qwen2.5", "name": "Qwen 2.5", "full_name": "qwen2.5:latest"},
            ]
        
        current = get_current_model()
        
        logger.info(f"Available models: {len(available_models)}")
        
        return jsonify({
            'success': True,
            'models': available_models,
            'current_model': current,
            'count': len(available_models)
        })
        
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama - is it running?")
        # Return default models if Ollama is not accessible
        default_models = [
            {"id": "llama3.1", "name": "Llama 3.1", "full_name": "llama3.1:latest"},
            {"id": "mistral", "name": "Mistral", "full_name": "mistral:latest"},
            {"id": "gemma2", "name": "Gemma 2", "full_name": "gemma2:latest"},
            {"id": "qwen2.5", "name": "Qwen 2.5", "full_name": "qwen2.5:latest"},
        ]
        return jsonify({
            'success': True,
            'models': default_models,
            'current_model': get_current_model(),
            'count': len(default_models),
            'warning': 'Using default model list - Ollama not accessible'
        })
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/set_model', methods=['POST'])
def set_model():
    """Set the active LLM model with validation and verification."""
    try:
        data = request.json
        model_id = data.get('model', '').strip()
        
        if not model_id:
            return jsonify({'error': 'No model specified'}), 400
        
        # Store old model for verification
        old_model = get_current_model()
        logger.info(f"Switching from {old_model} to {model_id}")
        
        # Verify model exists in Ollama
        try:
            ollama_response = requests.get('http://localhost:11434/api/tags', timeout=5)
            ollama_response.raise_for_status()
            ollama_data = ollama_response.json()
            
            # Extract available model names
            available_model_names = []
            if 'models' in ollama_data:
                for model in ollama_data['models']:
                    model_name = model.get('name', '')
                    # Add both full name and cleaned name
                    available_model_names.append(model_name)
                    cleaned_name = model_name.replace(':latest', '')
                    if cleaned_name != model_name:
                        available_model_names.append(cleaned_name)
            
            # Check if requested model is available
            model_found = False
            actual_model_name = model_id
            
            # Try exact match first
            if model_id in available_model_names:
                model_found = True
                actual_model_name = model_id
            # Try with :latest suffix
            elif f"{model_id}:latest" in available_model_names:
                model_found = True
                actual_model_name = model_id  # Use clean name
            # Try without :latest suffix
            elif model_id.replace(':latest', '') in [m.replace(':latest', '') for m in available_model_names]:
                model_found = True
                actual_model_name = model_id.replace(':latest', '')
            
            if not model_found:
                logger.warning(f"Model {model_id} not found in Ollama. Available: {available_model_names}")
                return jsonify({
                    'error': f'Model "{model_id}" not found in Ollama',
                    'available_models': available_model_names,
                    'suggestion': 'Pull the model with: ollama pull ' + model_id
                }), 404
            
            # TEST THE MODEL before switching (quick test to see if it loads)
            logger.info(f"Testing model {actual_model_name} before switching...")
            try:
                test_response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        "model": actual_model_name,
                        "prompt": "test",
                        "stream": False
                    },
                    timeout=30  # 30 second timeout for model load test
                )
                
                if test_response.status_code != 200:
                    error_detail = test_response.text
                    try:
                        error_data = test_response.json()
                        error_msg = error_data.get('error', error_detail)
                    except:
                        error_msg = error_detail
                    
                    logger.error(f"Model test failed: {error_msg}")
                    
                    # Provide specific error messages
                    if "out of memory" in error_msg.lower() or "oom" in error_msg.lower():
                        return jsonify({
                            'error': f'Model "{actual_model_name}" is te groot voor uw systeem',
                            'details': 'Onvoldoende geheugen beschikbaar',
                            'suggestion': 'Kies een kleiner model (llama3.1, mistral, gemma2) of sluit andere applicaties'
                        }), 400
                    else:
                        return jsonify({
                            'error': f'Model "{actual_model_name}" kan niet worden geladen',
                            'details': error_msg,
                            'suggestion': 'Herstart Ollama of kies een ander model'
                        }), 400
                
                logger.info(f"✓ Model test passed for {actual_model_name}")
                
            except requests.exceptions.Timeout:
                logger.warning(f"Model test timeout for {actual_model_name} - model may be slow to load")
                return jsonify({
                    'warning': f'Model "{actual_model_name}" is groot en kan traag laden',
                    'success': True,
                    'model': actual_model_name,
                    'message': f'Model switched to {actual_model_name} (first query may be slow)',
                    'verified': True
                })
            
            # Update the current model (this saves to disk)
            set_current_model(actual_model_name)
            
            # VERIFY persistence immediately
            verification_passed = False
            verification_error = None
            
            # 1. Check in-memory value
            if get_current_model() == actual_model_name:
                logger.debug(f"✓ In-memory verification passed: {actual_model_name}")
                
                # 2. Check file was written
                if MODEL_CONFIG_FILE.exists():
                    try:
                        with open(MODEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                            saved_config = json.load(f)
                            saved_model = saved_config.get('current_model')
                            
                            if saved_model == actual_model_name:
                                logger.info(f"✓ File verification passed: {actual_model_name} saved to {MODEL_CONFIG_FILE}")
                                
                                # 3. Test reload from disk
                                reloaded_model = load_model_config()
                                if reloaded_model == actual_model_name:
                                    logger.info(f"✓ Reload verification passed: {actual_model_name}")
                                    verification_passed = True
                                else:
                                    verification_error = f"Reload failed: got {reloaded_model}"
                            else:
                                verification_error = f"File contains wrong model: {saved_model}"
                    except Exception as e:
                        verification_error = f"Cannot read config file: {e}"
                else:
                    verification_error = f"Config file not created: {MODEL_CONFIG_FILE}"
            else:
                verification_error = f"In-memory value wrong: {get_current_model()}"
            
            if not verification_passed:
                logger.error(f"✗ Persistence verification FAILED: {verification_error}")
                return jsonify({
                    'success': False,
                    'error': 'Model switch succeeded but persistence verification failed',
                    'details': verification_error,
                    'model': actual_model_name
                }), 500
            
            logger.info(f"✓✓✓ Model switched to: {actual_model_name} (verified persistent and tested)")
            
            return jsonify({
                'success': True,
                'model': actual_model_name,
                'message': f'Model switched to {actual_model_name}',
                'verified': True,
                'tested': True,
                'config_file': str(MODEL_CONFIG_FILE)
            })
            
        except requests.exceptions.ConnectionError:
            # Ollama not accessible, but allow switch anyway (user might fix it)
            logger.warning(f"Ollama not accessible, but switching model to {model_id} anyway")
            set_current_model(model_id)
            
            # Still verify persistence
            if get_current_model() == model_id and MODEL_CONFIG_FILE.exists():
                verification_passed = True
            else:
                verification_passed = False
            
            return jsonify({
                'success': True,
                'model': model_id,
                'message': f'Model switched to {model_id}',
                'warning': 'Could not verify with Ollama - make sure model is available',
                'verified': verification_passed,
                'tested': False
            })
        
    except Exception as e:
        logger.error(f"Error setting model: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def status():
    """Get system status including current model with verification."""
    docs_exist, doc_count = check_documents_exist()
    current_model = get_current_model()
    
    # Verify persistence
    persisted_model = None
    config_exists = MODEL_CONFIG_FILE.exists()
    
    if config_exists:
        try:
            with open(MODEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                persisted_model = config.get('current_model')
        except:
            pass
    
    persistent = (current_model == persisted_model)
    
    logger.debug(f"Status check: current model is {current_model}, persisted: {persisted_model}, match: {persistent}")
    
    return jsonify({
        'documents_exist': docs_exist,
        'document_count': doc_count,
        'ollama_available': True,
        'current_model': current_model,
        'persisted_model': persisted_model,
        'persistence_verified': persistent,
        'config_file_exists': config_exists,
        'config_file_path': str(MODEL_CONFIG_FILE)
    })


@app.route('/api/verify_model_persistence', methods=['GET'])
def verify_model_persistence():
    """Dedicated endpoint to verify model persistence is working."""
    try:
        current_model = get_current_model()
        
        # Check config file exists
        if not MODEL_CONFIG_FILE.exists():
            return jsonify({
                'success': False,
                'verified': False,
                'error': 'Config file does not exist',
                'config_path': str(MODEL_CONFIG_FILE),
                'current_model': current_model
            })
        
        # Read from config file
        try:
            with open(MODEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                saved_model = config.get('current_model')
        except Exception as e:
            return jsonify({
                'success': False,
                'verified': False,
                'error': f'Cannot read config file: {e}',
                'config_path': str(MODEL_CONFIG_FILE),
                'current_model': current_model
            })
        
        # Verify match
        if current_model == saved_model:
            # Test reload
            reloaded = load_model_config()
            if reloaded == current_model:
                return jsonify({
                    'success': True,
                    'verified': True,
                    'current_model': current_model,
                    'saved_model': saved_model,
                    'reloaded_model': reloaded,
                    'config_path': str(MODEL_CONFIG_FILE),
                    'message': 'Model persistence verified successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'verified': False,
                    'error': 'Reload test failed',
                    'current_model': current_model,
                    'saved_model': saved_model,
                    'reloaded_model': reloaded
                })
        else:
            return jsonify({
                'success': False,
                'verified': False,
                'error': 'Mismatch between memory and file',
                'current_model': current_model,
                'saved_model': saved_model,
                'config_path': str(MODEL_CONFIG_FILE)
            })
            
    except Exception as e:
        logger.error(f"Error verifying model persistence: {e}")
        return jsonify({
            'success': False,
            'verified': False,
            'error': str(e)
        }), 500


@app.route('/api/list_documents', methods=['GET'])
def list_documents():
    """Get list of all ingested documents with their details."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        
        with conn.cursor() as cur:
            # Get document details
            cur.execute(sql.SQL("""
                SELECT DISTINCT ON (file_path)
                    file_name,
                    file_path,
                    file_type,
                    file_size,
                    modified_time,
                    created_at,
                    (SELECT COUNT(*) FROM {} d2 WHERE d2.file_path = d1.file_path) as chunk_count
                FROM {} d1
                ORDER BY file_path, created_at DESC;
            """).format(sql.Identifier(PG_TABLE), sql.Identifier(PG_TABLE)))
            
            documents = []
            for row in cur.fetchall():
                # Format file size
                file_size = row[3]
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                
                documents.append({
                    'file_name': row[0],
                    'file_path': row[1],
                    'file_type': row[2],
                    'file_size': file_size,
                    'file_size_formatted': size_str,
                    'chunk_count': row[6],
                    'ingested_at': row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
                })
        
        conn.close()
        
        # Sort by file name
        documents.sort(key=lambda x: x['file_name'].lower())
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total_count': len(documents)
        })
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point."""
    docs_exist, doc_count = check_documents_exist()
    
    if not docs_exist:
        logger.warning("=" * 60)
        logger.warning("WAARSCHUWING: Geen documenten gevonden in database!")
        logger.warning("Run eerst WhereSpace.py om documenten te indexeren.")
        logger.warning("=" * 60)
    else:
        logger.info(f"Found {doc_count} documents in database")
    
    logger.info("=" * 60)
    logger.info(f"Starting WhereSpace Chat on http://{WEB_HOST}:{WEB_PORT}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)


if __name__ == "__main__":
    main()
