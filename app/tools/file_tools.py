"""
File Tools - Tools để thao tác với files.
"""
from typing import Optional
from langchain_core.tools import tool


@tool
def write_file_tool(file_path: str, content: str) -> str:
    """
    Ghi nội dung vào file.
    
    Args:
        file_path: Đường dẫn file cần ghi (ví dụ: output.txt, data.json)
        content: Nội dung cần ghi vào file
        
    Returns:
        Thông báo kết quả ghi file
    """
    try:
        import os
        from pathlib import Path
        
        # Tạo thư mục nếu chưa tồn tại
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Ghi file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"File đã được ghi thành công: {file_path}"
    except Exception as e:
        return f"Lỗi khi ghi file {file_path}: {str(e)}"

