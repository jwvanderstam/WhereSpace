# Web Interface Migration Plan

## Overview
Migrate all terminal-based functionality to a modern web interface with proper navigation and page structure.

## New Page Structure

### 1. Chat Interface (/) - **DONE**
- Main chat with RAG/Direct modes
- Model selector in top bar
- Document count badge
- Real-time streaming responses

### 2. Documents Page (/documents)
**Purpose**: View and manage indexed documents

**Features**:
- List all indexed documents with stats
- Sort by name, size, date, chunks
- Filter by file type
- Delete individual documents
- Bulk operations (delete all)
- Document details modal

**UI Components**:
- Data table with search
- File type badges
- Size indicators
- Chunk count
- Action buttons

### 3. Document Indexing Page (/ingest)
**Purpose**: Index new documents

**Features**:
- Directory browser/input
- File type filter
- Progress bar with real-time updates
- Success/error notifications
- Recent indexing history
- Batch status

**UI Components**:
- Path input with validation
- File type checkboxes
- Drag & drop zone (future)
- Progress indicator
- Result summary

### 4. Storage Analysis Page (/storage)
**Purpose**: Analyze local storage

**Features**:
- Directory scanner
- Category breakdown (pie chart)
- Size statistics
- Top directories list
- File type distribution
- Document discovery

**UI Components**:
- Directory input
- Charts (Chart.js)
- Statistics cards
- Directory tree view
- Export results button

### 5. Model Management Page (/models)
**Purpose**: Manage Ollama models

**Features**:
- List installed models
- Model statistics
- Download new models
- Delete models
- Model information
- Test model loading

**UI Components**:
- Model cards with actions
- Download modal with progress
- Confirmation dialogs
- Model details panel
- Family grouping

### 6. RAG Evaluation Page (/evaluation)
**Purpose**: Evaluate RAG performance

**Features**:
- Run evaluation tests
- Hit rate metrics
- MRR (Mean Reciprocal Rank)
- Query examples
- Results visualization
- Historical comparison

**UI Components**:
- Start evaluation button
- Progress indicator
- Results dashboard
- Charts for metrics
- Query examples table

### 7. Settings Page (/settings)
**Purpose**: Configuration and deployment

**Features**:
- Database settings
- Ollama configuration
- Model preferences
- Deployment settings
- System info
- Logs viewer

**UI Components**:
- Tabbed interface
- Form inputs
- Save/Reset buttons
- Connection test buttons
- Log viewer panel

---

## Implementation Steps

### Phase 1: Core Structure ?
- [x] Create base.html template
- [x] Add navigation sidebar
- [x] Update index.html to extend base

### Phase 2: New Routes (WhereSpaceChat.py)
```python
@app.route('/documents')
def documents_page():
    \"\"\"Documents management page\"\"\"
    return render_template('documents.html')

@app.route('/ingest')
def ingest_page():
    \"\"\"Document indexing page\"\"\"
    return render_template('ingest.html')

@app.route('/storage')
def storage_page():
    \"\"\"Storage analysis page\"\"\"
    return render_template('storage.html')

@app.route('/models')
def models_page():
    \"\"\"Model management page\"\"\"
    return render_template('models.html')

@app.route('/evaluation')
def evaluation_page():
    \"\"\"RAG evaluation page\"\"\"
    return render_template('evaluation.html')

@app.route('/settings')
def settings_page():
    \"\"\"Settings and deployment page\"\"\"
    return render_template('settings.html')
```

### Phase 3: API Endpoints for New Features

#### Storage Analysis
```python
@app.route('/api/storage/scan', methods=['POST'])
def scan_storage_api():
    \"\"\"Scan directory and return results\"\"\"
    directory = request.json.get('directory')
    # Call WhereSpace.scan_storage()
    # Return JSON results

@app.route('/api/storage/analyze', methods=['POST'])
def analyze_storage_api():
    \"\"\"Analyze storage and return statistics\"\"\"
    # Return categories, sizes, file types
```

#### Model Management (Already exists, enhance)
```python
# Already have:
# - GET /api/models
# - POST /api/set_model

# Add:
@app.route('/api/models/<model_name>/info', methods=['GET'])
def get_model_details(model_name):
    \"\"\"Get detailed model information\"\"\"

@app.route('/api/models/<model_name>/test', methods=['POST'])
def test_model(model_name):
    \"\"\"Test if model loads successfully\"\"\"
```

#### Evaluation
```python
@app.route('/api/evaluation/run', methods=['POST'])
def run_evaluation():
    \"\"\"Run RAG evaluation\"\"\"
    # Stream progress updates
    def generate():
        # Yield progress as SSE
        pass
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/evaluation/results', methods=['GET'])
def get_evaluation_results():
    \"\"\"Get latest evaluation results\"\"\"
```

### Phase 4: HTML Templates

Create templates for each page extending base.html:
- `templates/documents.html`
- `templates/ingest.html`
- `templates/storage.html`
- `templates/models.html`
- `templates/evaluation.html`
- `templates/settings.html`

### Phase 5: JavaScript Modules

Create modular JavaScript files:
- `static/chat.js` - Chat functionality
- `static/documents.js` - Document management
- `static/ingest.js` - Indexing logic
- `static/storage.js` - Storage analysis
- `static/models.js` - Model management
- `static/evaluation.js` - Evaluation logic

### Phase 6: Simplify main.py

```python
# New simplified main.py
def main():
    \"\"\"Launch web interface directly\"\"\"
    print("=" * 60)
    print("    JW zijn babbeldoos - AI Document Chat System")
    print("=" * 60)
    print()
    print("Starting web interface...")
    print("Navigate to: http://127.0.0.1:5000")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    from WhereSpaceChat import main as start_server
    start_server()

if __name__ == "__main__":
    main()
```

---

## UI/UX Improvements

### Navigation
- Sidebar with icons and labels
- Active page highlighting
- Breadcrumbs for sub-pages
- Quick actions in top bar

### Consistency
- Unified color scheme
- Consistent button styles
- Standard card layouts
- Common modal patterns

### Responsiveness
- Mobile-friendly sidebar
- Responsive tables
- Touch-friendly buttons
- Adaptive layouts

### User Feedback
- Toast notifications
- Progress indicators
- Loading states
- Error messages with suggestions

---

## Benefits

### For Users
? **No Terminal Required** - Everything in browser
? **Better UX** - Visual, intuitive interface
? **Real-time Updates** - Progress bars, live stats
? **Multi-tasking** - Multiple tabs/pages
? **Accessible** - Works from any device
? **Professional** - Modern, polished look

### For Development
? **Maintainable** - Modular structure
? **Extensible** - Easy to add features
? **Testable** - Clear API boundaries
? **Deployable** - Web-based, easy to deploy

---

## Migration Timeline

1. **Phase 1**: Core structure (Base template, navigation) - **DONE**
2. **Phase 2**: Flask routes (All page routes) - 2 hours
3. **Phase 3**: API endpoints (Backend logic) - 3 hours
4. **Phase 4**: HTML templates (All pages) - 4 hours
5. **Phase 5**: JavaScript (Interactivity) - 3 hours
6. **Phase 6**: Testing and polish - 2 hours

**Total Estimated Time**: 14 hours

---

## Next Steps

1. Complete Flask routes for all pages
2. Create HTML templates for each page
3. Implement JavaScript for interactivity
4. Test all functionality
5. Update README with new interface
6. Remove old terminal UI from main.py

Would you like me to continue with any specific page implementation?
