import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://hr_user:hr_password@postgres/hr_assistant')
    
    # Model Provider Selection - CHANGE THIS TO SWITCH!
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'deepseek').lower()  # openai, deepseek, or gemini
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # DeepSeek Settings
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    # Gemini Settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # Embeddings (always use OpenAI - cheapest option)
    OPENAI_API_KEY_FOR_EMBEDDINGS = os.getenv('OPENAI_API_KEY_FOR_EMBEDDINGS', '')
    
    # LangSmith settings (optional)
    LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY', '')
    LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'hr_policy_assistant')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    def get_current_provider_info(self):
        """Get info about current provider for debugging"""
        return {
            "provider": self.LLM_PROVIDER,
            "models": {
                "openai": self.OPENAI_MODEL,
                "deepseek": self.DEEPSEEK_MODEL,
                "gemini": self.GEMINI_MODEL
            }
        }
    
config = Config()