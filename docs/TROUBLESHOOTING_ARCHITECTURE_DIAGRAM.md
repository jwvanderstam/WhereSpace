# Troubleshooting: Architecture Diagram Not Loading

**Date:** December 26, 2025  
**Issue:** Architecture diagram not rendering on `/architecture` page  
**Status:** ?? **TROUBLESHOOTING**

---

## Problem

The architecture page loads but the Mermaid diagram doesn't render. The loading spinner shows "Diagram laden..." but nothing appears.

---

## Common Causes

### 1. **Mermaid.js Library Not Loading**

**Check:** Browser console for errors like:
```
Failed to load resource: net::ERR_INTERNET_DISCONNECTED
or
ReferenceError: mermaid is not defined
```

**Fix:** Check internet connection (Mermaid loads from CDN)

---

### 2. **Mermaid Syntax Error**

**Check:** Browser console for:
```
Error: Parse error on line X
```

**Fix:** Simplify diagram syntax

**Current minimal version:**
```javascript
const diagramCode = `graph LR
    A[Client] --> B[Flask Server]
    B --> C[PostgreSQL]
    B --> D[Ollama]
    C --> E[pgvector]
    D --> F[LLM Models]
    
    style A fill:#e1f5ff,stroke:#01579b
    style B fill:#f3e5f5,stroke:#4a148c
    style C fill:#fce4ec,stroke:#880e4f
    style D fill:#e8f5e9,stroke:#1b5e20
    style E fill:#fce4ec,stroke:#880e4f
    style F fill:#e8f5e9,stroke:#1b5e20`;
```

---

### 3. **JavaScript Errors**

**Check:** Browser DevTools Console (F12) for any errors

**Added:** Enhanced error logging:
```javascript
console.log('Starting diagram render...');
// ... rendering code ...
console.error('Error rendering diagram:', error);
```

---

### 4. **Content Security Policy (CSP)**

**Check:** Console for CSP violations

**Solution:** Add to base.html `<head>`:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; 
               style-src 'self' 'unsafe-inline';">
```

---

## Debugging Steps

### **Step 1: Open Browser Console**

1. Navigate to http://127.0.0.1:5000/architecture
2. Press **F12** to open Developer Tools
3. Click **Console** tab
4. Look for errors or messages

### **Step 2: Check Network Tab**

1. In DevTools, click **Network** tab
2. Reload page (F5)
3. Look for failed requests (red lines)
4. Check if `mermaid@10/dist/mermaid.min.js` loads successfully

### **Step 3: Test Mermaid Manually**

In browser console, type:
```javascript
typeof mermaid
```

**Expected:** `"object"` or `"function"`  
**If:** `"undefined"` ? Mermaid didn't load

### **Step 4: Test Diagram Rendering**

In console, try:
```javascript
mermaid.render('test', 'graph LR\nA-->B')
```

**Expected:** Returns SVG code  
**If error:** Check error message

---

## Quick Fixes

### **Fix 1: Use Local Mermaid (if CDN blocked)**

Download Mermaid and serve locally:

```bash
# Download Mermaid
curl -o static/mermaid.min.js https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
```

Change in `architecture.html`:
```html
<!-- Replace CDN -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<!-- With local -->
<script src="{{ url_for('static', filename='mermaid.min.js') }}"></script>
```

---

### **Fix 2: Fallback Static Image**

If dynamic rendering fails, show static image:

```html
<div id="mermaid-container" class="mermaid-diagram">
    <img src="{{ url_for('static', filename='architecture-diagram.png') }}" 
         alt="Architecture Diagram" 
         style="max-width: 100%; height: auto;">
</div>
```

---

### **Fix 3: Simplest Possible Diagram**

Test with absolute minimal code:

```javascript
const diagramCode = `graph LR
    A --> B`;
```

If this works, gradually add more complexity.

---

## Current Implementation Status

### **? What's Working:**

- ? Template loads without errors
- ? Page renders HTML correctly
- ? All sections display (Overview, Details, etc.)
- ? Error handling added
- ? Console logging added
- ? Simplified diagram syntax

### **?? What to Check:**

- [ ] Mermaid.js loads from CDN
- [ ] Browser console shows no errors
- [ ] Network tab shows successful requests
- [ ] Diagram renders in container

---

## Testing Checklist

When the page loads:

### **Visual Checks:**
- [ ] Page title shows "System Architectuur"
- [ ] Sidebar navigation visible
- [ ] "System Overzicht" section displays
- [ ] Performance metrics show (6-8x, 3-5x, etc.)
- [ ] "Architectuur Diagram" section present
- [ ] Zoom controls visible (Zoom In, Zoom Out, Reset)

### **Diagram Container:**
- [ ] Shows "Diagram laden..." initially
- [ ] OR shows rendered diagram
- [ ] OR shows error message with details

### **Browser Console (F12):**
- [ ] `Starting diagram render...` logged
- [ ] `Mermaid loaded, rendering diagram...` logged
- [ ] `Diagram rendered successfully` logged
- [ ] OR error message with details

---

## Error Messages & Solutions

### **"Mermaid library not loaded"**

**Cause:** CDN request failed  
**Solution:** 
1. Check internet connection
2. Try different browser
3. Use local Mermaid file

### **"Parse error on line X"**

**Cause:** Invalid Mermaid syntax  
**Solution:** 
1. Check diagram code for typos
2. Use simplified version
3. Test at https://mermaid.live/

### **"SecurityError: Blocked a frame with origin"**

**Cause:** CSP policy blocking script  
**Solution:** Add CSP meta tag (see above)

### **Container shows loading spinner forever**

**Cause:** JavaScript not executing  
**Solution:** 
1. Check browser console for errors
2. Verify Mermaid loaded
3. Check if JavaScript blocked

---

## Alternative: Static Diagram

If dynamic rendering continues to fail, create static diagram:

### **Option 1: Screenshot**
1. Use online tool: https://mermaid.live/
2. Paste diagram code
3. Export as PNG/SVG
4. Save to `static/architecture-diagram.png`

### **Option 2: Manual Diagram**
1. Create diagram in Draw.io or Lucidchart
2. Export as SVG
3. Embed in template

---

## Expected Console Output (Working)

```
Starting diagram render...
Mermaid loaded, rendering diagram...
Diagram rendered successfully
Architecture diagram displayed successfully
```

## Expected Console Output (Error)

```
Starting diagram render...
Error rendering diagram: [Error details]
Error details: [Message]
Diagram code: [Code]
```

---

## Files Modified

### **templates/architecture.html**

**Changes:**
1. ? Simplified Mermaid diagram (6 nodes instead of 40+)
2. ? Added console logging for debugging
3. ? Enhanced error handling
4. ? Error message shows details

---

## Next Steps

1. **Start application:**
   ```bash
   python main.py
   ```

2. **Open page:**
   http://127.0.0.1:5000/architecture

3. **Open DevTools:**
   Press F12

4. **Check Console tab:**
   Look for messages starting with "Starting diagram render..."

5. **Report findings:**
   - What messages appear?
   - Any errors?
   - Does diagram render?

---

## Quick Test Commands

### **Test 1: Template Syntax**
```bash
python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('templates')); env.get_template('architecture.html'); print('OK')"
```

### **Test 2: Flask Route**
```bash
python -c "from WhereSpaceChat import app; client = app.test_client(); r = client.get('/architecture'); print(f'Status: {r.status_code}')"
```

### **Test 3: Mermaid CDN**
```bash
curl -I https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
```

---

## Summary

**Status:** Implemented troubleshooting improvements  
**Next:** Test in browser with DevTools open  
**Expected:** Console logs will show where rendering fails  
**Fallback:** Can use static image if dynamic rendering doesn't work  

---

**Key Point:** The page itself works fine. The issue is specifically with the Mermaid.js diagram rendering, which requires:
1. Internet connection (for CDN)
2. JavaScript enabled
3. Valid Mermaid syntax
4. No CSP blocking

With the added logging, we can identify exactly which step fails.

---

*Last Updated: December 26, 2025*
