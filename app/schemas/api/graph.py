"""
Graph API Schemas - Schemas cho việc gọi SimpleGraph qua FastAPI.
"""
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class SimpleGraphRequest(BaseModel):
    """
    Request schema cho SimpleGraph endpoint.

    Attributes:
        query: Câu hỏi / input của user cho LLM.
        messages: (Optional) Lịch sử hội thoại trước đó, nếu muốn giữ context.
    """

    query: str = Field(..., description="User query/input", min_length=1)
    messages: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Optional conversation history for context",
    )


class SimpleGraphResult(BaseModel):
    """
    Kết quả thực thi SimpleGraph.

    Attributes:
        final_response: Câu trả lời cuối cùng từ graph.
        messages: Toàn bộ lịch sử hội thoại sau khi graph chạy.
        token_usage: Thống kê token (nếu có).
    """

    final_response: str = Field(..., description="Final response from the graph")
    messages: List[Dict[str, str]] = Field(
        ..., description="Conversation messages after graph execution"
    )
    token_usage: Dict[str, Any] = Field(
        default_factory=dict,
        description="Token usage statistics (prompt, completion, total)",
    )


class SimpleGraphResponse(BaseModel):
    """
    Response schema cho SimpleGraph endpoint.

    Attributes:
        success: Trạng thái thực thi.
        message: Mô tả trạng thái (thành công / lỗi).
        data: Payload kết quả SimpleGraph (nếu thành công).
    """

    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[SimpleGraphResult] = Field(
        default=None,
        description="SimpleGraph result payload",
    )


