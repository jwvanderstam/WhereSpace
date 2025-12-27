# Quick Fix: Add Navigation Menu

## Problem
The current `index.html` is standalone and doesn't show the navigation menu created in `base.html`.

## Option 1: Add Simple Menu Bar (Quick Fix)
Add a menu bar at the top of the current page without breaking anything.

## Option 2: Migrate to Base Template (Complete Fix)
Make `index.html` extend `base.html` properly - but this requires careful testing.

## Recommended: Option 1 (Quick Fix)

Add this to the top of the existing page (after header):

```html
<div class="quick-nav">
    <a href="/" class="nav-item active">?? Chat</a>
    <span class="nav-item disabled">?? Documenten (Coming Soon)</span>
    <span class="nav-item disabled">?? Indexeren (Use button below)</span>
    <span class="nav-item disabled">?? Analyse (Coming Soon)</span>
    <span class="nav-item disabled">?? Modellen (Use selector above)</span>
    <span class="nav-item disabled">?? Evaluatie (Coming Soon)</span>
    <span class="nav-item disabled">?? Instellingen (Coming Soon)</span>
</div>
```

```css
.quick-nav {
    background: white;
    padding: 10px 30px;
    display: flex;
    gap: 15px;
    border-bottom: 2px solid #f0f0f0;
    flex-wrap: wrap;
}

.quick-nav .nav-item {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    text-decoration: none;
    transition: all 0.3s;
}

.quick-nav .nav-item.active {
    background: #667eea;
    color: white;
}

.quick-nav .nav-item.disabled {
    color: #999;
    cursor: not-allowed;
    opacity: 0.5;
}

.quick-nav a.nav-item:not(.disabled):hover {
    background: #f0f0f0;
    color: #667eea;
}
```

This will give you a navigation bar showing:
- ? Chat (active/working)
- ?? Other pages (coming soon)
- ?? Hints where to find features

## To Implement Full Navigation

When you're ready for the complete navigation sidebar:

1. Create placeholder routes in `WhereSpaceChat.py`:
```python
@app.route('/documents')
def documents_page():
    return render_template('coming_soon.html', page='Documenten')

@app.route('/ingest')
def ingest_page():
    return render_template('coming_soon.html', page='Indexeren')
# ... etc
```

2. Create `templates/coming_soon.html`:
```html
{% extends "base.html" %}
{% block title %}{{ page }} - Coming Soon{% endblock %}
{% block page_title %}{{ page }}{% endblock %}
{% block content %}
<div class="card">
    <h2>?? {{ page }} - Coming Soon</h2>
    <p>This page is under development.</p>
    <p>For now, use the Chat interface and the buttons/modals available there.</p>
    <a href="/" class="btn btn-primary">Back to Chat</a>
</div>
{% endblock %}
```

3. Then all navigation links will work (pointing to coming soon pages).

Would you like me to implement either of these options?
