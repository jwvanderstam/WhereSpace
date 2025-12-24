# Persistent Model Switching - Implementation Guide

## ?? **Problem Solved**

**Before:** Model selection was reset to `llama3.1` every time the server restarted or page was refreshed.

**After:** Selected model is now **persistently stored** and remembered across:
- ? Server restarts
- ? Page refreshes
- ? Browser sessions
- ? Multiple tabs

---

## ?? **Implementation**

### **Dual Persistence Strategy**

We use **two layers of persistence** for maximum reliability:

1. **Server-side**: JSON config file (`.model_config.json`)
2. **Client-side**: Browser localStorage

---

## ?? **Server-Side Persistence**

### **Configuration File**

**Location:** `.model_config.json` (in same directory as `WhereSpaceChat.py`)

**Format:**
```json
{
  "current_model": "mistral",
  "updated_at": "C:\\Users\\...\\WhereSpace"
}
```

### **Implementation** (`WhereSpaceChat.py`)

```python
# Model persistence file
MODEL_CONFIG_FILE = Path(__file__).parent / ".model_config.json"

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
    
    return "llama3.1"  # Default

def save_model_config(model_id: str):
    """Save model configuration to disk for persistence."""
    try:
        config = {
            'current_model': model_id,
            'updated_at': str(Path.cwd())
        }
        with open(MODEL_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.debug(f"Saved model config: {model_id}")
    except Exception as e:
        logger.warning(f"Could not save model config: {e}")

# Load on startup
_current_model = load_model_config()

def set_current_model(model_id):
    """Set the current LLM model and persist it."""
    global _current_model
    _current_model = model_id
    save_model_config(model_id)  # Persist to disk
    logger.info(f"Model switched to: {model_id} (persisted)")
```

**Benefits:**
- ? Survives server restarts
- ? Works across different users (if shared server)
- ? Simple JSON format
- ? Easy to edit manually if needed

---

## ?? **Client-Side Persistence**

### **Browser localStorage**

**Key:** `selectedModel`
**Value:** Model ID (e.g., `"mistral"`)

### **Implementation** (`templates/index.html`)

```javascript
// On model load
async function loadModels() {
    const response = await fetch('/api/models');
    const data = await response.json();
    
    if (data.success) {
        currentModel = data.current_model;
        
        // Save to localStorage
        localStorage.setItem('selectedModel', currentModel);
        
        // Populate dropdown with current model selected
        // ...
    }
}

// On model switch
async function switchModel() {
    const selectedModel = modelSelector.value;
    
    const response = await fetch('/api/set_model', {
        method: 'POST',
        body: JSON.stringify({ model: selectedModel })
    });
    
    if (data.success) {
        currentModel = selectedModel;
        
        // Save to localStorage for session persistence
        localStorage.setItem('selectedModel', currentModel);
        
        console.log('? Model switched and persisted:', selectedModel);
    }
}

// On page load
async function initializeModels() {
    // Restore from localStorage first (instant)
    const savedModel = localStorage.getItem('selectedModel');
    if (savedModel) {
        currentModel = savedModel;
        console.log(`Pre-loaded model from localStorage: ${currentModel}`);
    }
    
    // Then sync with server
    await loadModels();
}
```

**Benefits:**
- ? Instant restoration (no API call needed)
- ? Per-user preference (in their browser)
- ? Works offline (until sync needed)
- ? Survives page refreshes

---

## ?? **How It Works**

### **Scenario 1: First Time User**

```
User opens page
  ?
Frontend checks localStorage ? None found
  ?
Frontend calls GET /api/models
  ?
Backend loads .model_config.json ? "llama3.1" (default)
  ?
Frontend receives: current_model = "llama3.1"
  ?
Frontend saves to localStorage: "llama3.1"
  ?
Dropdown shows: Llama 3.1 selected
```

### **Scenario 2: User Switches Model**

```
User selects "Mistral" from dropdown
  ?
Frontend calls POST /api/set_model {"model": "mistral"}
  ?
Backend updates _current_model = "mistral"
Backend saves to .model_config.json
  ?
Backend returns: {"success": true}
  ?
Frontend saves to localStorage: "mistral"
Frontend shows: "Model switched to mistral"
  ?
All subsequent queries use mistral
```

### **Scenario 3: Server Restart**

```
Server restarts
  ?
Backend loads .model_config.json on startup
  ?
_current_model = "mistral" (from file)
  ?
Server ready with mistral as current model
  ?
User's next query uses mistral automatically ?
```

### **Scenario 4: Page Refresh**

```
User refreshes page (Ctrl+R or F5)
  ?
Frontend checks localStorage ? "mistral"
Frontend sets currentModel = "mistral" (instant)
  ?
Frontend calls GET /api/models
  ?
Backend returns: current_model = "mistral"
  ?
Dropdown shows: Mistral selected ?
```

### **Scenario 5: New Browser Tab**

```
User opens new tab
  ?
localStorage is shared across tabs (same origin)
  ?
Frontend checks localStorage ? "mistral"
  ?
Frontend syncs with server
  ?
Both tabs use mistral ?
```

---

## ?? **Testing**

### **Test 1: Model Persists After Server Restart**

```bash
# 1. Start server
python WhereSpaceChat.py

# 2. Switch to mistral via web UI
# http://127.0.0.1:5000

# 3. Stop server (Ctrl+C)

# 4. Restart server
python WhereSpaceChat.py

# 5. Check logs
# Expected: "INFO - Loaded saved model: mistral"

# 6. Open web UI
# Expected: Mistral is selected in dropdown
```

### **Test 2: Model Persists After Page Refresh**

```javascript
// 1. Open browser console
console.log('Before:', localStorage.getItem('selectedModel'));

// 2. Switch to gemma2 via dropdown

// 3. Check localStorage
console.log('After:', localStorage.getItem('selectedModel'));
// Expected: "gemma2"

// 4. Refresh page (F5)

// 5. Check dropdown
// Expected: Gemma 2 is selected

// 6. Check localStorage
console.log('After refresh:', localStorage.getItem('selectedModel'));
// Expected: "gemma2"
```

### **Test 3: Verify Config File**

```bash
# 1. Switch model via web UI

# 2. Check config file
cat .model_config.json

# Expected output:
{
  "current_model": "mistral",
  "updated_at": "C:\\Users\\...\\WhereSpace"
}

# 3. Edit file manually
# Change "mistral" to "gemma2"

# 4. Restart server

# 5. Open web UI
# Expected: Gemma 2 is selected
```

### **Test 4: Multiple Tabs**

```
# 1. Open tab A: http://127.0.0.1:5000
# 2. Open tab B: http://127.0.0.1:5000

# 3. In tab A: Switch to mistral

# 4. In tab B: Refresh page

# Expected: Tab B now shows mistral selected
```

---

## ?? **Persistence Flow Diagram**

```
???????????????????????????????????????????????????
?           USER ACTION: Select Model             ?
???????????????????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ?  Frontend: onChange event  ?
        ??????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? POST /api/set_model        ?
        ? {"model": "mistral"}       ?
        ??????????????????????????????
                     ?
                     ?
        ??????????????????????????????????????
        ? Backend: set_current_model()       ?
        ?  1. Update _current_model variable ?
        ?  2. Call save_model_config()       ?
        ??????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????????????
        ? Save to .model_config.json         ?
        ? {"current_model": "mistral", ...}  ?
        ??????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? Return success to frontend ?
        ??????????????????????????????
                     ?
                     ?
        ??????????????????????????????????????
        ? Frontend: localStorage.setItem()   ?
        ? Key: "selectedModel"               ?
        ? Value: "mistral"                   ?
        ??????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? Update UI: Show badge      ?
        ? Display: "mistral"         ?
        ??????????????????????????????


????????????????????????????????????????????????????
?        SERVER RESTART / PAGE RELOAD              ?
????????????????????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? Backend: On startup        ?
        ? load_model_config()        ?
        ??????????????????????????????
                     ?
                     ?
        ??????????????????????????????????????
        ? Read .model_config.json            ?
        ? ? _current_model = "mistral"       ?
        ??????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? Frontend: On page load     ?
        ? initializeModels()         ?
        ??????????????????????????????
                     ?
                     ?
        ??????????????????????????????????????
        ? Check localStorage                 ?
        ? ? currentModel = "mistral"         ?
        ??????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? GET /api/models            ?
        ??????????????????????????????
                     ?
                     ?
        ??????????????????????????????????????
        ? Backend returns:                   ?
        ? {"current_model": "mistral", ...}  ?
        ??????????????????????????????????????
                     ?
                     ?
        ??????????????????????????????
        ? Frontend: Select "mistral" ?
        ? in dropdown                ?
        ??????????????????????????????
```

---

## ??? **Error Handling**

### **Config File Missing**

```python
def load_model_config():
    if MODEL_CONFIG_FILE.exists():
        # Load from file
    else:
        # Return default
        return "llama3.1"
```

**Result:** Falls back to default model

### **Config File Corrupted**

```python
try:
    with open(MODEL_CONFIG_FILE, 'r') as f:
        config = json.load(f)
except Exception as e:
    logger.warning(f"Could not load model config: {e}")
    return "llama3.1"
```

**Result:** Logs warning, uses default

### **localStorage Not Available**

```javascript
try {
    localStorage.setItem('selectedModel', currentModel);
} catch (e) {
    console.warn('localStorage not available:', e);
    // Continue without localStorage
}
```

**Result:** Still works, just without client-side persistence

### **Server-Client Mismatch**

```javascript
// Frontend tries to restore "codellama"
const savedModel = localStorage.getItem('selectedModel');

// But server has "mistral" (codellama was uninstalled)
const serverModel = data.current_model;

// Solution: Server always wins
currentModel = serverModel;
localStorage.setItem('selectedModel', serverModel);
```

**Result:** Server state is source of truth

---

## ?? **File Locations**

```
WhereSpace/
??? WhereSpaceChat.py          # Backend with persistence logic
??? .model_config.json         # Server-side storage (created automatically)
??? templates/
?   ??? index.html             # Frontend with localStorage
??? .gitignore                 # Add .model_config.json here
```

### **Add to .gitignore**

```bash
# User preferences (not committed to git)
.model_config.json
```

---

## ?? **Debugging**

### **Check Current Model**

**Server-side:**
```bash
# View config file
cat .model_config.json

# Check logs
# Look for: "Loaded saved model: ..."
```

**Client-side:**
```javascript
// In browser console
console.log('Current model:', currentModel);
console.log('localStorage:', localStorage.getItem('selectedModel'));

// Check server
fetch('/api/status')
    .then(r => r.json())
    .then(data => console.log('Server model:', data.current_model));
```

### **Force Reset**

**Server-side:**
```bash
# Delete config file
rm .model_config.json

# Restart server
python WhereSpaceChat.py
# Will use default: llama3.1
```

**Client-side:**
```javascript
// In browser console
localStorage.removeItem('selectedModel');
location.reload();
```

---

## ? **Benefits Summary**

| Feature | Before | After |
|---------|--------|-------|
| **Server restart** | Reset to llama3.1 | Remembers selection ? |
| **Page refresh** | Reset to llama3.1 | Remembers selection ? |
| **Multiple tabs** | Independent | Shared selection ? |
| **Manual edit** | Not possible | Edit .model_config.json ? |
| **Offline mode** | No persistence | localStorage works ? |

---

## ?? **Result**

Your model selection is now **fully persistent** across:
- ? Server restarts
- ? Page refreshes  
- ? Browser sessions
- ? Multiple tabs
- ? Different users (server-side)

**No more resetting to llama3.1 every time!** ??

---

*Last Updated: December 24, 2025*
