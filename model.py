# Model script - to be implemented based on user guidance 

import os
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
import openai

class ModelManager:
    """Manages different LLM providers with environment-based configuration."""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model_name = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
    def get_model(self) -> BaseLLM:
        """
        Get the configured LLM model based on environment variables.
        
        Returns:
            BaseLLM: Configured language model instance
        """
        if self.provider == "openai":
            return self._get_openai_model()
        elif self.provider == "gemini":
            return self._get_gemini_model()
        elif self.provider == "anthropic":
            return self._get_anthropic_model()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _get_openai_model(self) -> ChatOpenAI:
        """Get OpenAI model with environment-based configuration."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL"),  # For custom endpoints
            organization=os.getenv("OPENAI_ORGANIZATION")
        )
    
    def _get_gemini_model(self) -> ChatGoogleGenerativeAI:
        """Get Google Gemini model with environment-based configuration."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=api_key
        )
    
    def _get_anthropic_model(self) -> ChatAnthropic:
        """Get Anthropic Claude model with environment-based configuration."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        return ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            anthropic_api_key=api_key
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently configured model.
        
        Returns:
            Dict[str, Any]: Model configuration information
        """
        return {
            "provider": self.provider,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "api_key_configured": self._is_api_key_configured()
        }
    
    def _is_api_key_configured(self) -> bool:
        """Check if the required API key is configured for the current provider."""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY", 
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        required_key = key_mapping.get(self.provider)
        if not required_key:
            return False
        
        return bool(os.getenv(required_key))

# Global model manager instance
model_manager = ModelManager()

def get_model() -> BaseLLM:
    """
    Get the configured LLM model.
    
    Returns:
        BaseLLM: Configured language model instance
    """
    return model_manager.get_model()

def get_model_config() -> Dict[str, Any]:
    """
    Get the current model configuration.
    
    Returns:
        Dict[str, Any]: Model configuration information
    """
    return model_manager.get_model_info() 