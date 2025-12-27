# ?? WhereSpace - Quick Start Guide

## What Changed?

**? Old files renamed to `.old` extension**  
**? New unified structure working**  
**? Clean, maintainable code**

---

## ?? **Start the Application (3 Ways)**

### **Method 1: Startup Script (Easiest)**
```powershell
# Just double-click or run:
start.bat
```

### **Method 2: Command Line**
```powershell
cd "C:\Users\Gebruiker\source\repos\WhereSpace"
python app.py
```

### **Method 3: Python Module**
```powershell
python -m app
```

**Then open:** `http://127.0.0.1:5000`

---

## ?? **New Structure**

```
WhereSpace/
??? app.py               ? Main application (NEW!)
??? config.py            ? Configuration
??? start.bat            ? Quick start script
?
??? services/            ? Business logic
?   ??? database_service.py
?   ??? llm_service.py
?   ??? model_service.py
?   ??? document_service.py
?
??? templates/           ? UI templates
?   ??? layout.html      ? Base (sidebar + topbar)
?   ??? dashboard.html   ? Homepage
?   ??? architecture.html
?
??? *.old                ? Old files (archived)
```

---

## ? **What Works**

- ? **Dashboard** - Modern homepage with stats
- ? **Sidebar** - Persistent navigation
- ? **Model Selector** - Real Ollama models
- ? **Chat Panel** - Slides in from right
- ? **Architecture** - System diagram
- ? **Documents** - List & manage docs
- ? **API Endpoints** - Full REST API

---

## ?? **Old Files (Archived)**

These files were renamed but preserved:
- `WhereSpaceChat.py.old` - Old monolithic app
- `templates/index.html.old` - Old chat interface
- `templates/base.html.old` - Old base template
- `main.py.old` - Old entry point

**You can delete them if not needed.**

---

## ?? **Verify It Works**

```powershell
# Test services
python -c "from app import create_app; app = create_app(); print('? OK')"
```

**Should see:**
```
INFO - Database connection pool initialized
INFO - Loaded saved model: llama3.1
INFO - All services initialized successfully
? OK
```

---

## ?? **Documentation**

- `docs/CLEANUP_COMPLETE.md` - Full cleanup details
- `docs/UNIFIED_APP_READY.md` - Quick start
- `docs/TOPBAR_AND_CHAT_FIXED.md` - Service details
- `docs/RESTRUCTURING_PLAN.md` - Architecture plan

---

## ? **Quick Commands**

```powershell
# Start app
python app.py

# Test database
python -c "from services import DatabaseService; print('DB OK')"

# Test Ollama
curl http://localhost:11434/api/tags
```

---

## ?? **Ready!**

Just run `start.bat` or `python app.py` and you're good to go!

**Everything works!** ?
