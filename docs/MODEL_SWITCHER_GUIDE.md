# JW zijn babbeldoos - Feature Update

## Changes Made

### 1. Rebranding
- **Application Name**: Changed from "WhereSpace Chat" to "JW zijn babbeldoos"
- **Page Title**: Updated to "JW zijn babbeldoos - AI Chat Interface"
- **Welcome Message**: Updated empty state to show new branding

### 2. Model Switcher Feature

#### Backend (`WhereSpaceChat.py`)
- Added `AVAILABLE_MODELS` configuration with multiple LLM options:
  - **Llama 3.1** (default) - Fast, general purpose
  - **Mistral** - Balanced performance
  - **Gemma 2** - Google's model
  - **Qwen 2.5** - Strong reasoning

- New API endpoints:
  - `GET /api/models` - Returns list of available models
  - `POST /api/set_model` - Switches active model
  - Updated `/api/status` - Now includes current model

#### Frontend (`templates/index.html`)
- **Model Selector Dropdown**:
  - Located in header next to document counter
  - Shows all available models with descriptions
  - Styled to match application theme
  - Real-time model switching without page reload

- **Model Badge**:
  - Each AI response shows which model was used
  - Small badge next to mode indicator (RAG/Direct)
  - Helps track which model gave which answer

- **Visual Feedback**:
  - System message confirms model switch
  - Current model persists in dropdown selection
  - Model badge in conversation shows active model

## How to Use

### Switching Models
1. Click the model dropdown in the header
2. Select desired model (e.g., "Mistral - Balanced performance")
3. System message confirms switch
4. All new queries use selected model
5. Model badge shows which model answered

### Model Selection Tips
- **Llama 3.1**: Best for general questions, fastest
- **Mistral**: Good balance of speed and quality
- **Gemma 2**: Google's model, good for technical queries
- **Qwen 2.5**: Best reasoning, slower but more thorough

### Before Using New Models
Make sure to pull them with Ollama:
```bash
ollama pull mistral
ollama pull gemma2
ollama pull qwen2.5
```

## Technical Details

### State Management
- Current model stored in JavaScript variable `currentModel`
- Synced with backend via API calls
- Persists across mode switches (RAG/Direct)
- Visible in each AI response via badge

### API Flow
1. Page loads ? `GET /api/models` ? Populates dropdown
2. User selects model ? `POST /api/set_model` ? Backend updates
3. Next query uses new model
4. Response shows model badge

### Styling
- Model selector matches header theme
- Translucent background with backdrop blur
- Hover effects for better UX
- Model badge color-coded by mode

## Features Overview

### Header Components (Left to Right)
1. **Title**: "JW zijn babbeldoos"
2. **Model Selector**: Dropdown with available LLMs
3. **Document Counter**: Click to view ingested documents

### Toolbar
- **Mode Toggle**: RAG Mode / Direct LLM
- **Indexeer Directory**: Add more documents
- **Verwijder Alle Documenten**: Clear database

### Chat Features
- Mode badge shows RAG/Direct/System
- Model badge shows which LLM (llama3.1, mistral, etc.)
- Source citations in RAG mode
- Real-time streaming responses

## Example Workflow

1. **Select Model**: Choose "Mistral" from dropdown
2. **Choose Mode**: Click "RAG Mode"
3. **Ask Question**: "Wat staat er in mijn documenten over belasting?"
4. **See Response**: 
   - Badge shows: `RAG Mode` `mistral`
   - Answer with source citations
   - Can compare by switching models

## Benefits

? **Flexibility**: Try different models for same question
? **Transparency**: Always know which model answered
? **Comparison**: Easy to compare model outputs
? **Personalization**: Use your preferred model
? **Performance**: Switch to faster/slower models as needed

## Future Enhancements

Potential additions:
- Model performance metrics
- Model comparison side-by-side
- Per-document model preferences
- Temperature/parameter controls
- Model-specific optimizations

## Troubleshooting

### Model not available
**Error**: "Invalid model: modelname"
**Solution**: Pull model with `ollama pull modelname`

### Dropdown shows old models
**Solution**: Refresh page or check `/api/models` endpoint

### Model switch not working
**Check**: 
1. Ollama is running
2. Model is pulled locally
3. Check browser console for errors
4. Verify API endpoint responds

## Testing Checklist

- [ ] Model dropdown populates on page load
- [ ] Can switch between all models
- [ ] System message confirms switch
- [ ] New queries use selected model
- [ ] Model badge shows in responses
- [ ] Model persists across mode switches
- [ ] Multiple models can be tested in sequence
- [ ] Page title shows "JW zijn babbeldoos"

Enjoy your personalized "babbeldoos"! ??
