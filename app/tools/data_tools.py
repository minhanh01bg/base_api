"""
Data Tools - Tools để đọc dữ liệu.
"""
from typing import Optional
from langchain_core.tools import tool


@tool
def read_data_tool(file_path: str) -> str:
    """
    Đọc nội dung file.
    
    Args:
        file_path: Đường dẫn file cần đọc
        
    Returns:
        Nội dung file hoặc thông báo lỗi
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"Nội dung file {file_path}:\n\n{content}"
    except FileNotFoundError:
        return f"File không tồn tại: {file_path}"
    except Exception as e:
        return f"Lỗi khi đọc file {file_path}: {str(e)}"

