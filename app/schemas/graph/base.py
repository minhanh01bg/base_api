"""
Base Graph State Schemas - Base TypedDict cho LangGraph states.

Các graph state schemas định nghĩa cấu trúc dữ liệu được truyền qua
các nodes trong LangGraph workflow.
"""
from typing import TypedDict, Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BaseGraphState(TypedDict, total=False):
    """
    Base state cho tất cả graphs.
    
    Attributes:
        messages: Danh sách messages trong conversation
        query: User query/input
        final_response: Final response từ graph
        token_usage: Token usage statistics
        human_input: Input từ human trong human-in-the-loop (optional)
        waiting_for_human: Flag cho biết graph đang chờ human input
        intent: Intent type - "question" hoặc "request" (để quyết định có vào human-in-the-loop không)
        file_content: Nội dung file cần ghi (nếu intent là "request")
        file_path: Đường dẫn file cần ghi (nếu intent là "request")
    """
    messages: List[Dict[str, str]]
    query: str
    final_response: str
    token_usage: Dict[str, Any]
    human_input: Optional[str]
    waiting_for_human: bool
    intent: Optional[str]  # "question" hoặc "request"
    file_content: Optional[str]
    file_path: Optional[str]

class IntentClassification(BaseModel):
    """
    Intent classification schema.
    
    Attributes:
        intent: Intent type - "question" hoặc "request"
    """
    intent: str = Field(..., description="Intent type - 'question' or 'request'")


class FileInfo(BaseModel):
    """
    File information schema - Trích xuất từ user query.
    
    Attributes:
        file_name: Tên file (chỉ tên file, không bao gồm đường dẫn)
        file_content: Nội dung file cần ghi
    """
    file_name: str = Field(..., description="Tên file cần ghi (ví dụ: output.txt, data.json, notes.md) - chỉ tên file, không có đường dẫn")
    file_content: str = Field(..., description="Nội dung file cần ghi")