"""
LLM Factory - Makes it easy to switch between different model providers
Just change LLM_PROVIDER in .env file!
"""
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from .config import config
import os

class LLMFactory:
    """Factory class to create LLM instances based on configuration"""
    
    @staticmethod
    def create_llm(temperature=0, model_name=None):
        """
        Create an LLM instance based on LLM_PROVIDER in .env
        
        Args:
            temperature: Controls randomness (0 = deterministic)
            model_name: Optional specific model name (uses default if None)
        
        Returns:
            LangChain chat model instance
        """
        provider = config.LLM_PROVIDER.lower()
        
        if provider == "openai":
            return LLMFactory._create_openai(temperature, model_name)
        elif provider == "deepseek":
            return LLMFactory._create_deepseek(temperature, model_name)
        elif provider == "gemini":
            return LLMFactory._create_gemini(temperature, model_name)
        else:
            # Default to deepseek if not specified
            print(f"⚠️ Unknown provider '{provider}', defaulting to deepseek")
            return LLMFactory._create_deepseek(temperature, model_name)
    
    @staticmethod
    def _create_openai(temperature, model_name=None):
        """Create OpenAI LLM"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env")
        
        return ChatOpenAI(
            model=model_name or "gpt-3.5-turbo",
            temperature=temperature,
            api_key=config.OPENAI_API_KEY
        )
    
    @staticmethod
    def _create_deepseek(temperature, model_name=None):
        """Create DeepSeek LLM"""
        if not config.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY not set in .env")
        
        return ChatDeepSeek(
            model=model_name or "deepseek-chat",
            temperature=temperature,
            api_key=config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
    
    @staticmethod
    def _create_gemini(temperature, model_name=None):
        """Create Google Gemini LLM"""
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        
        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-pro",
            temperature=temperature,
            google_api_key=config.GEMINI_API_KEY,
            convert_system_message_to_human=True  # Gemini needs this
        )


class EmbeddingFactory:
    """Factory for embeddings - still using OpenAI (cheapest option)"""
    
    @staticmethod
    def create_embeddings():
        """Create embeddings instance (always using OpenAI for now)"""
        from langchain_openai import OpenAIEmbeddings
        
        if not config.OPENAI_API_KEY_FOR_EMBEDDINGS and not config.OPENAI_API_KEY:
            raise ValueError("No OpenAI API key found for embeddings")
        
        # Use dedicated embeddings key if available, otherwise use main OpenAI key
        api_key = config.OPENAI_API_KEY_FOR_EMBEDDINGS or config.OPENAI_API_KEY
        
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-ada-002"  # Cheap and good
        )