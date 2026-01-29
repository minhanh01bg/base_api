"""
Base Graph classes - Abstract base classes cho graph implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver  # In-memory checkpointer cho test
from langchain_openai import ChatOpenAI

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import Settings

# Import at runtime to avoid circular imports
def _get_settings():
    from app.core.config import settings
    return settings

# Import BaseGraphState từ schemas
from app.schemas.graph.base import BaseGraphState


class BaseGraph(ABC):
    """
    Abstract base class cho tất cả graph implementations.
    
    Cung cấp:
    - LLM initialization
    - Graph building pattern
    - Checkpointer cho human-in-the-loop
    - Common utilities
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        checkpointer: Optional[Union[MemorySaver, InMemorySaver]] = None,
    ):
        """
        Initialize base graph.
        
        Args:
            llm: Pre-initialized LLM instance (optional)
            model_name: Model name (defaults to settings.openai_model)
            temperature: Temperature (defaults to settings.openai_temperature)
            checkpointer: Checkpointer instance (defaults to MemorySaver for testing)
        """
        settings = _get_settings()
        self.llm = llm or ChatOpenAI(
            model_name=model_name or settings.openai_model,
            temperature=temperature or settings.openai_temperature,
            openai_api_key=settings.get_openai_api_key(),
        )
        # Sử dụng MemorySaver cho test, có thể thay bằng AsyncPostgresSaver cho production
        # Hoặc InMemorySaver cho agent với HumanInTheLoopMiddleware
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()
    
    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """
        Build và compile graph.
        
        Returns:
            Compiled StateGraph instance
        """
        pass
    
    @abstractmethod
    async def invoke(self, state: BaseGraphState) -> Dict[str, Any]:
        """
        Invoke graph với state.
        
        Args:
            state: Initial state
            
        Returns:
            Final state after graph execution
        """
        pass

