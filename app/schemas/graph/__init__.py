"""
Graph Schemas - TypedDict definitions cho LangGraph state.

Các schemas này định nghĩa state structure cho LangGraph workflows.
Khác với API schemas, graph schemas sử dụng TypedDict vì:
- LangGraph yêu cầu TypedDict cho state
- State có thể được mutate trong graph execution
- Không cần validation như Pydantic (graph tự quản lý state)
"""

from .base import BaseGraphState

__all__ = [
    "BaseGraphState",
]

