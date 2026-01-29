"""
Graph API Routes - Endpoints để gọi SimpleGraph qua FastAPI.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_settings
from app.graph.simple_graph import SimpleGraph
from app.schemas.graph import BaseGraphState
from app.schemas.api import (
    SimpleGraphRequest,
    SimpleGraphResponse,
    SimpleGraphResult,
    SimpleGraphContinueRequest,
    SimpleGraphStatusResponse,
)

router = APIRouter()


@router.post("/simple/start", response_model=SimpleGraphResponse)
async def start_simple_graph(
    request: SimpleGraphRequest,
    settings=Depends(get_settings),
):
    """
    Bắt đầu SimpleGraph với human-in-the-loop.
    
    Graph sẽ chạy đến node human_review và pause để chờ human input.
    Trả về thread_id để có thể resume sau.

    Args:
        request: SimpleGraphRequest body.
        settings: App settings.

    Returns:
        SimpleGraphResponse với thread_id và waiting_for_human=True nếu bị interrupt.
    """
    try:
        import uuid
        
        # Khởi tạo graph instance
        graph = SimpleGraph()

        # Generate thread_id trước
        thread_id = str(uuid.uuid4())

        # Chuẩn bị initial state cho graph
        initial_state: BaseGraphState = {
            "messages": request.messages or [],
            "query": request.query,
            "final_response": "",
            "token_usage": {},
        }

        # Thực thi graph với thread_id
        result_state = await graph.invoke(initial_state, thread_id=thread_id)

        # Kiểm tra nếu graph bị interrupt (chờ human input)
        if "__interrupt__" in result_state:
            # Graph đã pause tại human_approval node (cho request) hoặc các node khác
            # Lấy thông tin file để user review (nếu có)
            file_path = result_state.get("file_path")
            file_content = result_state.get("file_content")
            
            # Tạo result với thông tin file để review
            review_data = None
            if file_path and file_content:
                review_data = SimpleGraphResult(
                    final_response=f"Yêu cầu ghi file:\n\nFile: {file_path}\n\nNội dung:\n{file_content}",
                    messages=result_state.get("messages", []),
                    token_usage=result_state.get("token_usage", {}) or {},
                    intent=result_state.get("intent"),
                    file_path=file_path,
                    file_content=file_content,
                )
            else:
                # Nếu không có file (có thể đang chờ ở ask_user_for_file_info)
                review_data = SimpleGraphResult(
                    final_response=result_state.get("final_response", "Đang chờ thông tin từ người dùng..."),
                    messages=result_state.get("messages", []),
                    token_usage=result_state.get("token_usage", {}) or {},
                    intent=result_state.get("intent"),
                    file_path=None,
                    file_content=None,
                )
            
            return SimpleGraphResponse(
                success=True,
                message="Graph paused, waiting for human approval to write file" if file_path else "Graph paused, waiting for human input",
                data=review_data,
                thread_id=thread_id,
                waiting_for_human=True,
            )

        # Graph đã chạy xong (không bị interrupt)
        result = SimpleGraphResult(
            final_response=result_state.get("final_response", ""),
            messages=result_state.get("messages", []),
            token_usage=result_state.get("token_usage", {}) or {},
            intent=result_state.get("intent"),
            file_path=result_state.get("file_path"),
            file_content=None,  # Không trả về content sau khi đã ghi file
        )

        return SimpleGraphResponse(
            success=True,
            message="SimpleGraph executed successfully",
            data=result,
            thread_id=thread_id,  # Luôn trả về thread_id để track conversation
            waiting_for_human=False,
        )
    except Exception as e:
        return SimpleGraphResponse(
            success=False,
            message=f"Error executing SimpleGraph: {str(e)}",
            data=None,
            thread_id=None,
            waiting_for_human=False,
        )


@router.post("/simple/{thread_id}/continue", response_model=SimpleGraphResponse)
async def continue_simple_graph(
    thread_id: str,
    request: SimpleGraphContinueRequest,
    settings=Depends(get_settings),
):
    """
    Resume SimpleGraph sau khi nhận human input.
    
    Sử dụng thread_id để resume graph từ checkpoint đã lưu.

    Args:
        thread_id: Thread ID từ lần invoke trước.
        request: SimpleGraphContinueRequest với human_input.
        settings: App settings.

    Returns:
        SimpleGraphResponse với kết quả sau khi resume.
    """
    try:
        # Khởi tạo graph instance (cùng checkpointer với lần trước)
        graph = SimpleGraph()

        # Resume graph với human_input
        result_state = await graph.invoke(
            state={},  # State sẽ được load từ checkpoint
            thread_id=thread_id,
            resume_value=request.human_input,
        )

        # Kiểm tra nếu graph vẫn bị interrupt (nếu có nhiều interrupt points)
        if "__interrupt__" in result_state:
            # Lấy thông tin file để user review (nếu có)
            file_path = result_state.get("file_path")
            file_content = result_state.get("file_content")
            final_response = result_state.get("final_response", "")
            
            # Tạo result với thông tin để review
            review_data = None
            if file_path and file_content:
                # human_approval stage
                review_data = SimpleGraphResult(
                    final_response=f"Yêu cầu ghi file:\n\nFile: {file_path}\n\nNội dung:\n{file_content}",
                    messages=result_state.get("messages", []),
                    token_usage=result_state.get("token_usage", {}) or {},
                    intent=result_state.get("intent"),
                    file_path=file_path,
                    file_content=file_content,
                )
            else:
                # ask_user_for_file_info stage
                review_data = SimpleGraphResult(
                    final_response=final_response or "Đang chờ thông tin từ người dùng...",
                    messages=result_state.get("messages", []),
                    token_usage=result_state.get("token_usage", {}) or {},
                    intent=result_state.get("intent"),
                    file_path=None,
                    file_content=None,
                )
            
            return SimpleGraphResponse(
                success=True,
                message="Graph paused again, waiting for more human input",
                data=review_data,
                thread_id=thread_id,
                waiting_for_human=True,
            )

        # Graph đã chạy xong
        result = SimpleGraphResult(
            final_response=result_state.get("final_response", ""),
            messages=result_state.get("messages", []),
            token_usage=result_state.get("token_usage", {}) or {},
            intent=result_state.get("intent"),
            file_path=result_state.get("file_path"),
            file_content=None,  # Không trả về content sau khi đã ghi file
        )

        return SimpleGraphResponse(
            success=True,
            message="Graph resumed and completed successfully",
            data=result,
            thread_id=thread_id,
            waiting_for_human=False,
        )
    except Exception as e:
        return SimpleGraphResponse(
            success=False,
            message=f"Error resuming graph: {str(e)}",
            data=None,
            thread_id=thread_id,
            waiting_for_human=False,
        )


@router.get("/simple/{thread_id}/status", response_model=SimpleGraphStatusResponse)
async def get_simple_graph_status(
    thread_id: str,
    settings=Depends(get_settings),
):
    """
    Xem trạng thái hiện tại của graph với thread_id.
    
    Args:
        thread_id: Thread ID để check status.
        settings: App settings.

    Returns:
        SimpleGraphStatusResponse với trạng thái hiện tại.
    """
    try:
        # TODO: Implement logic để lấy state từ checkpointer
        # Hiện tại chỉ return basic status
        return SimpleGraphStatusResponse(
            thread_id=thread_id,
            waiting_for_human=True,  # Assume đang chờ nếu có status endpoint
            current_state=None,
        )
    except Exception as e:
        # Return error status
        return SimpleGraphStatusResponse(
            thread_id=thread_id,
            waiting_for_human=False,
            current_state={"error": str(e)},
        )


@router.get("/simple/web", response_class=HTMLResponse)
async def simple_graph_web_ui():
    """
    Web UI đơn giản để test SimpleGraph với human-in-the-loop.
    
    Returns:
        HTML page để test graph (đọc từ file template)
    """
    import os
    from pathlib import Path
    
    # Lấy đường dẫn đến file template
    current_dir = Path(__file__).parent.parent.parent  # app/
    template_path = current_dir / "templates" / "simple_graph_web.html"
    
    # Đọc file HTML
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Template file not found: {template_path}</p>",
            status_code=404
        )


