"""
LLM Utilities - Helper functions cho LLM operations.
"""
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage

if TYPE_CHECKING:
    from app.core.config import Settings

# Import at runtime to avoid circular imports
def _get_settings():
    from app.core.config import settings
    return settings

try:
    from langchain_community.callbacks import get_openai_callback
except ImportError:
    from langchain.callbacks import get_openai_callback


def create_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
) -> ChatOpenAI:
    """
    Create LLM instance với default settings.
    
    Args:
        model_name: Model name (defaults to settings.openai_model)
        temperature: Temperature (defaults to settings.openai_temperature)
        api_key: OpenAI API key (defaults to settings.openai_api_key)
        
    Returns:
        ChatOpenAI instance
    """
    settings = _get_settings()
    return ChatOpenAI(
        model_name=model_name or settings.openai_model,
        temperature=temperature or settings.openai_temperature,
        openai_api_key=api_key or settings.get_openai_api_key(),
    )


def create_messages(
    system_prompt: Optional[str] = None,
    user_message: Optional[str] = None,
    conversation_history: Optional[List[BaseMessage]] = None,
) -> List[BaseMessage]:
    """
    Create message list cho LLM.
    
    Args:
        system_prompt: System prompt
        user_message: User message
        conversation_history: Previous conversation messages
        
    Returns:
        List of messages
    """
    messages = []
    
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    
    if conversation_history:
        messages.extend(conversation_history)
    
    if user_message:
        messages.append(HumanMessage(content=user_message))
    
    return messages


def format_token_usage(callback) -> Dict[str, Any]:
    """
    Format token usage từ OpenAI callback.
    
    Args:
        callback: OpenAI callback instance
        
    Returns:
        Token usage dictionary
    """
    if callback is None:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost": 0.0,
        }
    
    return {
        "prompt_tokens": callback.prompt_tokens,
        "completion_tokens": callback.completion_tokens,
        "total_tokens": callback.total_tokens,
        "cost": callback.total_cost if hasattr(callback, "total_cost") else 0.0,
    }

