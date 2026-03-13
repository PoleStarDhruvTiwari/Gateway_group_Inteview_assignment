from fastapi import APIRouter, Depends
from ..config import config
from .. import auth

router = APIRouter()

@router.get("/model-info")
async def get_model_info(current_user = Depends(auth.get_current_user)):
    """Get information about currently configured LLM provider"""
    return {
        "current_provider": config.LLM_PROVIDER,
        "models": {
            "openai": config.OPENAI_MODEL,
            "deepseek": config.DEEPSEEK_MODEL,
            "gemini": config.GEMINI_MODEL
        },
        "note": "Change LLM_PROVIDER in .env to switch models"
    }