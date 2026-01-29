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
        intent: Intent type - "question" hoặc "request" (nếu có).
        file_path: Đường dẫn file (nếu có yêu cầu ghi file).
        file_content: Nội dung file (nếu có yêu cầu ghi file).
    """

    final_response: str = Field(..., description="Final response from the graph")
    messages: List[Dict[str, str]] = Field(
        ..., description="Conversation messages after graph execution"
    )
    token_usage: Dict[str, Any] = Field(
        default_factory=dict,
        description="Token usage statistics (prompt, completion, total)",
    )
    intent: Optional[str] = Field(
        default=None,
        description="Intent type - 'question' or 'request'",
    )
    file_path: Optional[str] = Field(
        default=None,
        description="File path if file write was requested",
    )
    file_content: Optional[str] = Field(
        default=None,
        description="File content if file write was requested (for review before approval)",
    )


class SimpleGraphResponse(BaseModel):
    """
    Response schema cho SimpleGraph endpoint.

    Attributes:
        success: Trạng thái thực thi.
        message: Mô tả trạng thái (thành công / lỗi).
        data: Payload kết quả SimpleGraph (nếu thành công).
        thread_id: Thread ID để track conversation (cho human-in-the-loop).
        waiting_for_human: Flag cho biết graph đang chờ human input.
    """

    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[SimpleGraphResult] = Field(
        default=None,
        description="SimpleGraph result payload",
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="Thread ID for conversation tracking (human-in-the-loop)",
    )
    waiting_for_human: bool = Field(
        default=False,
        description="Flag indicating graph is waiting for human input",
    )


class SimpleGraphContinueRequest(BaseModel):
    """
    Request schema để resume graph sau interrupt.

    Attributes:
        human_input: Input từ human để tiếp tục graph.
    """

    human_input: str = Field(..., description="Human input to continue graph", min_length=1)


class SimpleGraphStatusResponse(BaseModel):
    """
    Response schema để xem trạng thái graph.

    Attributes:
        thread_id: Thread ID.
        waiting_for_human: Flag cho biết đang chờ human input.
        current_state: State hiện tại của graph (nếu có).
    """

    thread_id: str = Field(..., description="Thread ID")
    waiting_for_human: bool = Field(..., description="Flag indicating waiting for human input")
    current_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Current graph state (if available)",
    )


