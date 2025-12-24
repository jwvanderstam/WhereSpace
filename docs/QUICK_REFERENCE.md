# JW zijn babbeldoos - Quick Reference

## ?? Quick Start Commands

### Start Application
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Direct
python main.py
```

### Start Web Interface Only
```bash
python WhereSpaceChat.py
# Navigate to: http://127.0.0.1:5000
```

---

## ?? Menu Overview

| Option | Function | When to Use |
|--------|----------|-------------|
| **1** | Analyse opslag | Eerste keer, ontdek je documenten |
| **2** | Indexeer documenten | Nadat je weet waar documenten staan |
| **3** | Start webserver | Query je documenten met AI |
| **4** | Evalueer RAG | Check performance na indexering |
| **5** | View documenten | Zie wat er al geïndexeerd is |
| **0** | Afsluiten | Klaar |

---

## ?? Common Workflows

### First Time Setup
```
1. Start applicatie (start.bat)
2. Kies optie 1 (Analyseer opslag)
3. Scan je Documents folder
4. Noteer directories met belangrijke documenten
5. Kies optie 2 (Indexeer documenten)
6. Geef pad naar document directory op
7. Wacht op ingestion (2-5 min voor 20 docs)
8. Kies optie 3 (Start webserver)
9. Open http://127.0.0.1:5000 in browser
10. Begin met vragen stellen!
```

### Daily Use
```
1. Start applicatie
2. Kies optie 3 (Start webserver)
3. Query je documenten
```

### Add More Documents
```
1. Start applicatie
2. Kies optie 2 (Indexeer documenten)
3. Of via web interface: "Indexeer Directory"
```

---

## ?? Web Interface Shortcuts

| Feature | How To |
|---------|--------|
| **Switch Model** | Click dropdown in header |
| **View Documents** | Click document counter badge |
| **RAG vs Direct** | Toggle buttons in toolbar |
| **Add Documents** | "Indexeer Directory" button |
| **Clear All** | "Verwijder Alle Documenten" button |

---

## ?? Quick Tips

### Best Document Types
? PDF, DOCX, TXT, MD
? Images, Videos, Encrypted files

### Query Tips
- Specific questions work best
- Mention document names if known
- Try different models for comparison

### Performance
- First query = slow (cold start)
- Subsequent queries = fast
- 50 documents = optimal
- More documents = slower retrieval

---

## ?? Quick Fixes

### Ollama Not Running
```bash
ollama serve
```

### PostgreSQL Not Running
```bash
# Windows
net start postgresql-x64-14

# Docker
docker start postgres-container
```

### Port Already in Use
```bash
# Kill process on port 5000
# Windows: netstat -ano | findstr :5000
# Linux: lsof -ti:5000 | xargs kill
```

### Reset Everything
```sql
psql -d vectordb -c "DROP TABLE documents;"
# Then re-index documents
```

---

## ?? Status Checks

### Check Ollama
```bash
curl http://localhost:11434/api/tags
```

### Check PostgreSQL
```bash
psql -U postgres -d vectordb -c "SELECT COUNT(*) FROM documents;"
```

### Check Indexed Documents
```
Option 5 in main menu
OR
http://127.0.0.1:5000 ? Click document counter
```

---

## ?? Model Comparison

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| **Llama 3.1** | ??? | ??? | General questions |
| **Mistral** | ?? | ???? | Best all-around |
| **Gemma 2** | ?? | ???? | Technical docs |
| **Qwen 2.5** | ? | ????? | Complex analysis |

---

## ?? File Locations

| File | Purpose |
|------|---------|
| `main.py` | Main menu (start here) |
| `WhereSpaceChat.py` | Web server |
| `WhereSpace.py` | Document processing |
| `templates/index.html` | Web UI |
| `requirements.txt` | Dependencies |

---

## ?? Emergency Commands

### Kill Everything
```bash
# Windows
taskkill /F /IM python.exe

# Linux
pkill -f python
```

### Fresh Start
```bash
# 1. Drop database
psql -U postgres -c "DROP DATABASE vectordb;"
psql -U postgres -c "CREATE DATABASE vectordb;"

# 2. Restart Ollama
ollama serve

# 3. Start fresh
python main.py
```

---

## ?? Get Help

1. Check `TROUBLESHOOTING.md`
2. Check logs for errors
3. Verify Ollama + PostgreSQL running
4. Try fresh database
5. Check requirements installed

---

**Remember:** Start with small document set first! (10-20 files)
