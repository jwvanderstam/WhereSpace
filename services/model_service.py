# -*- coding: utf-8 -*-
"""
Model Service
Handles model management and persistence
"""
import logging
import json
from pathlib import Path
from typing import Optional
from config import get_config

logger = logging.getLogger(__name__)

class ModelService:
    """Service for model management"""
    
    def __init__(self, config=None):
        """Initialize model service"""
        if config is None:
            config = get_config()
        
        self.config = config
        self.config_file = config.MODEL_CONFIG_FILE
        self.current_model = self._load_model_config()
        
        # Ensure default model is persisted on first run
        if not self.config_file.exists():
            logger.info(f"First run detected - persisting default model: {self.current_model}")
            self._save_model_config(self.current_model)
    
    def _load_model_config(self) -> str:
        """Load saved model configuration from disk"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    model = config.get('current_model', self.config.DEFAULT_LLM_MODEL)
                    logger.info(f"Loaded saved model: {model}")
                    return model
        except Exception as e:
            logger.warning(f"Could not load model config: {e}")
        
        # Default model
        return self.config.DEFAULT_LLM_MODEL
    
    def _save_model_config(self, model_id: str):
        """Save model configuration to disk"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(exist_ok=True)
            
            config = {
                'current_model': model_id,
                'updated_at': str(Path.cwd())
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved model config: {model_id}")
        except Exception as e:
            logger.warning(f"Could not save model config: {e}")
    
    def get_current_model(self) -> str:
        """Get the current LLM model"""
        return self.current_model
    
    def set_current_model(self, model_id: str) -> bool:
        """Set the current LLM model and persist it"""
        try:
            self.current_model = model_id
            self._save_model_config(model_id)
            logger.info(f"Model switched to: {model_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting model: {e}")
            return False
    
    def verify_model_persistence(self) -> bool:
        """Verify that model persistence is working"""
        try:
            if not self.config_file.exists():
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                saved_model = config.get('current_model')
            
            return saved_model == self.current_model
        except Exception as e:
            logger.error(f"Error verifying persistence: {e}")
            return False
