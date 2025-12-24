# JW zijn babbeldoos ??

**AI-powered document chat system met RAG (Retrieval-Augmented Generation)**

Een complete oplossing voor het indexeren en bevragen van lokale documenten met AI, inclusief web interface en meerdere LLM modellen.

---

## ?? Features

### ?? Storage Analyse
- Recursief scannen van directories
- Categorisatie van bestanden (muziek, video's, documenten, etc.)
- Identificatie van documents geschikt voor indexering
- Overzicht van grootste mappen

### ?? Document Indexering
- Support voor: PDF, DOCX, TXT, MD, HTML, XML, JSON, CSV
- Intelligente text chunking met overlap
- High-quality embeddings via Ollama (nomic-embed-text)
- PostgreSQL + pgvector voor snelle similarity search
- Automatische deduplicatie

### ?? Web Chat Interface
- **RAG Mode**: Query geïndexeerde documenten met source citations
- **Direct LLM**: Algemene vragen zonder document context
- **Model Switcher**: Wissel tussen 4 LLM modellen (Llama 3.1, Mistral, Gemma 2, Qwen 2.5)
- Real-time streaming responses
- Document management (view, ingest, flush)
- Responsive modern UI

### ?? Evaluatie Tools
- Hit Rate en MRR (Mean Reciprocal Rank) metrics
- Test retrieval kwaliteit
- Track performance improvements over time

---

## ?? Quick Start

### Vereisten

1. **Python 3.8+**
2. **PostgreSQL met pgvector extensie**
3. **Ollama** met modellen:
   ```bash
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ollama pull mistral  # optioneel
   ollama pull gemma2   # optioneel
   ollama pull qwen2.5  # optioneel
   ```

### Installatie

1. **Clone repository:**
   ```bash
   cd C:\Users\Gebruiker\source\repos\WhereSpace
   ```

2. **Installeer dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL:**
   ```bash
   # Maak database
   createdb vectordb
   
   # Enable pgvector (wordt automatisch gedaan door script)
   psql -d vectordb -c "CREATE EXTENSION vector;"
   ```

4. **Start applicatie:**
   
   **Windows:**
   ```bash
   start.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **Of direct:**
   ```bash
   python main.py
   ```

---

## ?? Gebruik

### Hoofdmenu

```
============================================================
    JW zijn babbeldoos - AI Document Chat System
============================================================

HOOFDMENU
============================================================

1. ?? Analyseer lokale opslag
   - Scan directories voor bestanden
   - Bekijk storage verdeling
   - Identificeer documenten voor indexering

2. ?? Indexeer documenten
   - Selecteer directory met documenten
   - Extract en chunk tekst
   - Genereer embeddings en sla op

3. ?? Start web chat interface
   - RAG mode: Query geïndexeerde documenten
   - Direct LLM mode: Algemene vragen
   - Model switcher (4 modellen beschikbaar)

4. ?? Evalueer RAG performance
   - Test retrieval kwaliteit
   - Bekijk Hit Rate en MRR metrics

5. ?? Bekijk geïndexeerde documenten
   - Toon alle documenten in database
   - Bekijk chunk counts en details

0. ? Afsluiten
```

### Workflow

1. **Analyseer je opslag** (optie 1)
   - Scan je home directory of specifieke folder
   - Identificeer waar documenten staan
   - Bekijk storage statistieken

2. **Indexeer documenten** (optie 2)
   - Kies directory met belangrijke documenten
   - Wacht terwijl documenten worden verwerkt
   - Max 50 documenten (configureerbaar)

3. **Start web interface** (optie 3)
   - Ga naar http://127.0.0.1:5000
   - Stel vragen over je documenten (RAG mode)
   - Of gebruik Direct LLM voor algemene vragen
   - Wissel tussen modellen voor verschillende antwoorden

---

## ?? Web Interface Features

### RAG Mode
```
User: "Wat staat er in mijn documenten over belastingen?"

AI (llama3.1): Volgens [Bron 1: belastingaangifte_2024.pdf] moet je...

?? Bronnen:
  1. belastingaangifte_2024.pdf (relevance: 87.3%)
     Preview: "Voor het jaar 2024 zijn de volgende..."
```

### Model Switcher
Wissel tussen modellen voor verschillende antwoorden:
- **Llama 3.1**: Snel, algemeen
- **Mistral**: Gebalanceerd
- **Gemma 2**: Google's model, goed voor technisch
- **Qwen 2.5**: Sterk in reasoning

### Document Management
- **View**: Klik op document counter om lijst te zien
- **Ingest**: Indexeer meer documenten via web interface
- **Flush**: Verwijder alle geïndexeerde documenten

---

## ??? Configuratie

### Database (WhereSpaceChat.py)
```python
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "vectordb"
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"  # Verander dit!
```

### Chunking (WhereSpace.py)
```python
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 100  # Overlap tussen chunks
```

### Document Limit (WhereSpace.py)
```python
# In ingest_documents_to_pgvector()
if existing_count >= 50:  # Verhoog dit voor meer documenten
```

---

## ?? Project Structuur

```
WhereSpace/
??? main.py                      # ?? Hoofdmenu (START HIER)
??? start.bat / start.sh         # Quick start scripts
??? WhereSpace.py                # Storage analyse + document ingestion
??? WhereSpaceChat.py            # Web server + RAG backend
??? evaluate_rag.py              # Performance evaluatie
??? templates/
?   ??? index.html              # Web interface
??? requirements.txt             # Python dependencies
??? Documentation/
    ??? README.md               # Deze file
    ??? PERFORMANCE_GUIDE.md    # RAG optimalisaties
    ??? ROBUST_INGESTION.md     # Ingestion verbeteringen
    ??? MODEL_SWITCHER_GUIDE.md # Model switching
    ??? BUG_FIXES.md            # Recente fixes
    ??? TROUBLESHOOTING.md      # Probleemoplossing
```

---

## ?? Troubleshooting

### Ollama niet bereikbaar
```bash
# Check of Ollama draait
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### PostgreSQL connection errors
```bash
# Check of PostgreSQL draait
pg_isready

# Restart PostgreSQL (Windows)
net stop postgresql-x64-14
net start postgresql-x64-14

# Of via Docker
docker restart postgres-container
```

### "Invalid length of startup packet"
Dit is opgelost! De nieuwe versie gebruikt:
- Single persistent connection
- Proper error handling
- Retry logic met exponential backoff

### Module import errors
```bash
pip install -r requirements.txt
```

### Geen documenten gevonden
Check of:
- Directory path correct is
- Bestanden juiste extensie hebben (pdf, docx, txt, etc.)
- Bestanden niet te groot zijn (< 10MB)

---

## ?? Performance Tips

### Snelle Ingestion
- Start met kleine set documenten (10-20)
- Plain text files zijn snelst
- PDFs kunnen traag zijn (complex formatting)

### Betere Resultaten
- Gebruik specifieke vragen
- Probeer verschillende modellen
- Check source citations voor accuracy

### Database Onderhoud
```sql
-- Vacuum database
VACUUM ANALYZE documents;

-- Rebuild indexes
REINDEX TABLE documents;

-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('documents'));
```

---

## ?? Best Practices

### Document Selectie
? **Goed:**
- Belangrijke PDFs (contracten, rapporten)
- Word documenten (notes, artikelen)
- Markdown/text files (documentation)

? **Vermijd:**
- Zeer grote bestanden (> 10MB)
- Gescande documenten zonder OCR
- Password-protected files

### Query Formulering
? **Goed:**
```
"Wat zijn de deadline voor mijn belastingaangifte?"
"Geef een samenvatting van contract X"
"Wat staat er over prijzen in document Y?"
```

? **Vermijd:**
```
"Vertel me alles"  # Te vaag
"Wat is de hoofdstad van Frankrijk?"  # Niet in documenten (gebruik Direct mode)
```

### Model Keuze
- **Llama 3.1**: Snelle algemene vragen
- **Mistral**: Beste all-round
- **Gemma 2**: Technische documenten
- **Qwen 2.5**: Complexe analyse

---

## ?? Geavanceerde Features

### Custom Chunking
Pas `CHUNK_SIZE` en `CHUNK_OVERLAP` aan in `WhereSpace.py`:
```python
CHUNK_SIZE = 512  # Kleiner voor betere precision
CHUNK_OVERLAP = 100  # Meer overlap = meer context
```

### Custom Embeddings
Verander embedding model in `WhereSpace.py`:
```python
OLLAMA_EMBED_MODEL = "nomic-embed-text"  # Standaard
# Alternatieven:
# OLLAMA_EMBED_MODEL = "snowflake-arctic-embed"
# OLLAMA_EMBED_MODEL = "mxbai-embed-large"
```

### Evaluatie
Run periodic evaluaties:
```bash
python evaluate_rag.py
```

Target metrics:
- Hit Rate: > 80%
- MRR: > 0.7
- Avg Similarity: > 0.6

---

## ?? License

MIT License - See LICENSE file for details

---

## ????? Author

**JW** - AI Document Chat Enthusiast

---

## ?? Credits

Built with:
- [Ollama](https://ollama.ai/) - Local LLM inference
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [PostgreSQL](https://www.postgresql.org/) - Database

---

## ?? Support

Voor vragen of problemen:
1. Check `TROUBLESHOOTING.md`
2. Check `PERFORMANCE_GUIDE.md` voor optimalisatie tips
3. Review logs voor error messages
4. Check Ollama en PostgreSQL status

---

**Veel plezier met JW zijn babbeldoos! ??**
