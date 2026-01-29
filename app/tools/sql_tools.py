"""
SQL Tools - Tools để thực thi SQL queries.
"""
from typing import Optional
from langchain_core.tools import tool


@tool
def execute_sql_tool(query: str) -> str:
    """
    Thực thi SQL query trên database.
    
    Args:
        query: SQL query cần thực thi
        
    Returns:
        Kết quả query hoặc thông báo lỗi
    """
    try:
        from app.core.sql_database import get_sql_connector
        
        connector = get_sql_connector()
        if connector is None or connector.db is None:
            return "SQL database chưa được cấu hình. Vui lòng kiểm tra cấu hình database."
        
        # Thực thi query
        result = connector.db.run(query)
        return f"Query thực thi thành công:\n{result}"
    except Exception as e:
        return f"Lỗi khi thực thi SQL query: {str(e)}"

