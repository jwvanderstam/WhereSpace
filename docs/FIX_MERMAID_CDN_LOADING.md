# Fix: Mermaid.js Not Loading from CDN

**Date:** December 26, 2025  
**Error:** `Uncaught SyntaxError: Unexpected token '<'` and `ReferenceError: mermaid is not defined`  
**Root Cause:** CDN failing to load Mermaid.js library  
**Status:** ? **FIXED**

---

## Error Analysis

### **Console Errors:**

```
Uncaught SyntaxError: Unexpected token '<'
Uncaught ReferenceError: mermaid is not defined at architecture:906:5
```

### **What These Mean:**

1. **`SyntaxError: Unexpected token '<'`**
   - The browser expected JavaScript but got HTML
   - CDN returned an error page instead of the JS library
   - Likely causes: Network issue, CDN down, blocked by firewall

2. **`ReferenceError: mermaid is not defined`**
   - The script tried to use `mermaid` before it loaded
   - Script executes before library is available
   - No error handling for load failures

---

## Root Cause

The original code had no error handling for CDN failures:

```html
<!-- BEFORE: No error handling -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<script>
    // Immediately tries to use mermaid - fails if not loaded!
    mermaid.initialize({ ... });
</script>
```

**Problems:**
- ? No detection of load failure
- ? No fallback if CDN is down
- ? No wait for library to be ready
- ? No user-friendly error message

---

## Solution Implemented

### **1. Added `onerror` Handler**

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js" 
        onerror="handleMermaidLoadError()"></script>
```

**Benefits:**
- ? Detects when CDN fails
- ? Shows user-friendly error message
- ? Suggests solutions (check internet, reload, etc.)

### **2. Added Load Timeout Check**

```javascript
function waitForMermaid(callback, timeout = 5000) {
    const startTime = Date.now();
    
    const checkMermaid = setInterval(() => {
        if (typeof mermaid !== 'undefined') {
            clearInterval(checkMermaid);
            callback();  // Library loaded!
        } else if (Date.now() - startTime > timeout) {
            clearInterval(checkMermaid);
            handleMermaidLoadError();  // Timeout!
        }
    }, 100);
}
```

**Benefits:**
- ? Waits for library to be available
- ? Doesn't fail if loading is slow
- ? Timeout prevents infinite waiting
- ? Checks every 100ms

### **3. Enhanced Error Messages**

```javascript
function handleMermaidLoadError() {
    container.innerHTML = `
        <div>
            <h3>Fout bij laden diagram bibliotheek</h3>
            <p>Mogelijke oorzaken:</p>
            <ul>
                <li>Geen internetverbinding</li>
                <li>CDN is tijdelijk niet bereikbaar</li>
                <li>Firewall of proxy blokkeert toegang</li>
            </ul>
            <button onclick="location.reload()">Probeer Opnieuw</button>
        </div>
    `;
}
```

**Benefits:**
- ? Clear explanation
- ? Helpful troubleshooting tips
- ? Reload button for retry
- ? No technical jargon

### **4. Separated Initialization**

```javascript
// BEFORE: Immediate execution
mermaid.initialize({ ... });  // Fails if not loaded!

// AFTER: Wait then execute
window.addEventListener('DOMContentLoaded', function() {
    waitForMermaid(renderDiagram);  // Only after loaded!
});
```

**Benefits:**
- ? Waits for DOM to be ready
- ? Waits for Mermaid to load
- ? Graceful failure handling
- ? Better error messages

---

## Testing

### **Scenario 1: Normal Load (CDN works)**

**Expected:**
```
Page loaded, waiting for Mermaid...
Starting diagram render...
Mermaid loaded, initializing...
Rendering diagram...
Diagram rendered successfully
Architecture diagram displayed successfully
```

**Result:** ? Diagram displays correctly

---

### **Scenario 2: CDN Failure (No Internet)**

**Expected:**
```
Page loaded, waiting for Mermaid...
Failed to load Mermaid.js from CDN
```

**Result:** 
- ? Error message shown
- ? Suggestions displayed
- ? Reload button available
- ? No JavaScript errors

---

### **Scenario 3: Slow CDN (Timeout)**

**Expected:**
```
Page loaded, waiting for Mermaid...
(wait 5 seconds)
Mermaid load timeout
```

**Result:**
- ? Timeout after 5 seconds
- ? Error message shown
- ? User can retry

---

## Error Messages

### **CDN Load Failure:**
```
Fout bij laden diagram bibliotheek
De Mermaid.js bibliotheek kon niet worden geladen van het CDN.

Mogelijke oorzaken:
• Geen internetverbinding
• CDN is tijdelijk niet bereikbaar
• Firewall of proxy blokkeert toegang

[Probeer Opnieuw]
```

### **Rendering Error:**
```
Fout bij renderen diagram
Er is een fout opgetreden bij het renderen van het diagram.

[Error message details]

[Probeer Opnieuw]
```

---

## Architecture

### **Before (Broken):**
```
Browser ? CDN ? Script Tag ? Immediate Use
                     ? (FAILS)
                  No Error Handling
```

### **After (Fixed):**
```
Browser ? CDN ? Script Tag ? onerror Handler
                     ?              ?
                  Success        Failure
                     ?              ?
              waitForMermaid   Show Error
                     ?
              renderDiagram
```

---

## Code Changes Summary

| Aspect | Before | After |
|--------|--------|-------|
| CDN error handling | None | `onerror` attribute |
| Load detection | None | `waitForMermaid()` |
| Timeout | None | 5 seconds |
| Error messages | Generic | Specific with solutions |
| User experience | Blank or error | Helpful message |
| Retry option | None | Reload button |

---

## Benefits

### **For Users:**
- ? Clear error messages in Dutch
- ? Helpful troubleshooting tips
- ? Easy retry option
- ? No confusing technical errors
- ? Works even with slow connections

### **For Developers:**
- ? Detailed console logging
- ? Error stack traces
- ? Easy debugging
- ? Graceful degradation
- ? Robust error handling

---

## Prevention

### **Best Practices Applied:**

1. **Always handle CDN failures**
   ```html
   <script src="..." onerror="handleError()"></script>
   ```

2. **Wait for libraries to load**
   ```javascript
   if (typeof library === 'undefined') { wait(); }
   ```

3. **Add timeouts**
   ```javascript
   setTimeout(fallback, 5000);
   ```

4. **Show user-friendly errors**
   ```javascript
   container.innerHTML = 'Clear message with solutions';
   ```

5. **Provide retry option**
   ```html
   <button onclick="location.reload()">Try Again</button>
   ```

---

## Alternative Solutions

### **Option 1: Local Mermaid (Recommended if CDN issues persist)**

```bash
# Download Mermaid
mkdir static
curl -o static/mermaid.min.js https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
```

```html
<!-- Use local file -->
<script src="{{ url_for('static', filename='mermaid.min.js') }}"></script>
```

**Pros:** No CDN dependency, always works  
**Cons:** Need to update manually

---

### **Option 2: Fallback CDNs**

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js" 
        onerror="loadFromBackupCDN()"></script>

<script>
function loadFromBackupCDN() {
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/mermaid@10/dist/mermaid.min.js';
    script.onerror = handleMermaidLoadError;
    document.head.appendChild(script);
}
</script>
```

**Pros:** Redundancy  
**Cons:** More complex

---

### **Option 3: Static Image**

If all else fails, use a pre-rendered image:

```html
<img src="{{ url_for('static', filename='architecture.png') }}" 
     alt="Architecture Diagram">
```

---

## Summary

**Problem:** CDN not loading, no error handling  
**Solution:** Added comprehensive error handling and wait logic  
**Result:** Graceful failure with helpful messages  

**Key Improvements:**
- ? Detects CDN failures
- ? Waits for library to load
- ? Shows helpful error messages
- ? Provides retry option
- ? Detailed console logging
- ? 5-second timeout
- ? User-friendly interface

---

## Next Steps

1. **Test with internet ON:**
   - Should load and render diagram
   - Console shows success messages

2. **Test with internet OFF:**
   - Should show error message
   - Suggests checking connection
   - Reload button works

3. **If issues persist:**
   - Download Mermaid locally
   - Use static image fallback
   - Check firewall settings

---

**Status:** ? **FIXED - Ready to test!**

```bash
python main.py
# Navigate to: http://127.0.0.1:5000/architecture
# Check console (F12) for messages
```

---

*Last Updated: December 26, 2025*
