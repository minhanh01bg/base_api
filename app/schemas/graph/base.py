"""
Base Graph State Schemas - Base TypedDict cho LangGraph states.

Các graph state schemas định nghĩa cấu trúc dữ liệu được truyền qua
các nodes trong LangGraph workflow.
"""
from typing import TypedDict, Any, Dict, List


class BaseGraphState(TypedDict, total=False):
    """
    Base state cho tất cả graphs.
    
    Attributes:
        messages: Danh sách messages trong conversation
        query: User query/input
        final_response: Final response từ graph
        token_usage: Token usage statistics
    """
    messages: List[Dict[str, str]]
    query: str
    final_response: str
    token_usage: Dict[str, Any]

