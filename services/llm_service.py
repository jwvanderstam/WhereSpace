# -*- coding: utf-8 -*-
"""
LLM Service
Handles all Ollama interactions
"""
import logging
import requests
import json
from typing import List, Dict, Optional, Generator
from config import get_config

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations via Ollama"""
    
    def __init__(self, config=None):
        """Initialize LLM service"""
        if config is None:
            config = get_config()
        
        self.config = config
        self.base_url = config.OLLAMA_BASE_URL
        self.generate_url = config.OLLAMA_GENERATE_URL
        self.embed_url = config.OLLAMA_EMBED_URL
        self.tags_url = config.OLLAMA_TAGS_URL
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(self.tags_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            models = []
            if 'models' in data:
                for model in data['models']:
                    model_name = model.get('name', '')
                    # Clean up model name
                    display_name = model_name.replace(':latest', '')
                    base_name = display_name.split(':')[0] if ':' in display_name else display_name
                    
                    models.append({
                        'id': display_name,
                        'name': base_name.title(),
                        'full_name': model_name,
                        'size': model.get('size', 0),
                        'modified': model.get('modified_at', '')
                    })
            
            # Sort by name
            models.sort(key=lambda x: x['name'])
            logger.info(f"Found {len(models)} models in Ollama")
            return models
            
        except requests.exceptions.ConnectionError:
            logger.warning("Cannot connect to Ollama - is it running?")
            return []
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text"""
        try:
            payload = {
                "model": self.config.OLLAMA_EMBED_MODEL,
                "prompt": text
            }
            
            response = requests.post(self.embed_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get("embedding")
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_response_stream(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """Generate streaming response from LLM"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "top_p": self.config.DEFAULT_TOP_P,
                    "top_k": self.config.DEFAULT_TOP_K,
                    "num_ctx": self.config.MAX_CONTEXT_LENGTH
                }
            }
            
            response = requests.post(
                self.generate_url,
                json=payload,
                stream=stream,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama error: {response.status_code}"
                logger.error(error_msg)
                yield f"Error: {error_msg}"
                return
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                            elif 'error' in data:
                                yield f"\nError: {data['error']}"
                                return
                        except json.JSONDecodeError:
                            continue
            else:
                data = response.json()
                if 'response' in data:
                    yield data['response']
                elif 'error' in data:
                    yield f"Error: {data['error']}"
                    
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            yield "Error: Request timeout (model not responding)"
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama")
            yield "Error: Cannot connect to Ollama. Is it running?"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            yield f"Error: {str(e)}"
    
    def generate_rag_response_stream(
        self,
        query: str,
        context_chunks: List[Dict],
        model: str
    ) -> Generator[str, None, None]:
        """Generate RAG response with context"""
        # Build context with source attribution
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            similarity_pct = round(chunk.get('similarity', 0) * 100, 1)
            context_parts.append(
                f"[Bron {i}: {chunk['file_name']} (chunk {chunk['chunk_index']}, relevantie: {similarity_pct}%)]\n"
                f"{chunk['content']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Enhanced structured prompt
        prompt = f"""Je bent een nauwkeurige, professionele assistent die vragen beantwoordt op basis van documenten.

BELANGRIJKE REGELS:
1. Gebruik ALLEEN informatie uit de onderstaande bronnen
2. Citeer bronnen bij je antwoord (bijv. "Volgens [Bron 1]...")
3. Als de informatie niet in de bronnen staat, zeg dit duidelijk
4. Verzin GEEN informatie - blijf bij de feiten uit de documenten

BESCHIKBARE BRONNEN:
{context}

VRAAG: {query}

ANTWOORD:"""
        
        # Use the generate_response_stream method
        yield from self.generate_response_stream(prompt, model, temperature=0.2)
