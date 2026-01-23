"""
Graph API Routes - Endpoints để gọi SimpleGraph qua FastAPI.
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_settings
from app.graph.simple_graph import SimpleGraph
from app.schemas.graph import BaseGraphState
from app.schemas.api import SimpleGraphRequest, SimpleGraphResponse, SimpleGraphResult

router = APIRouter()


@router.post("/simple", response_model=SimpleGraphResponse)
async def invoke_simple_graph(
    request: SimpleGraphRequest,
    settings=Depends(get_settings),
):
    """
    Invoke SimpleGraph với query (và optional messages history).

    Args:
        request: SimpleGraphRequest body.
        settings: App settings (được inject để dễ mở rộng / logging / config).

    Returns:
        SimpleGraphResponse với final_response, messages, token_usage.
    """
    try:
        # Khởi tạo graph instance (LLM config lấy từ settings qua BaseGraph)
        graph = SimpleGraph()

        # Chuẩn bị initial state cho graph
        initial_state: BaseGraphState = {
            "messages": request.messages or [],
            "query": request.query,
            "final_response": "",
            "token_usage": {},
        }

        # Thực thi graph
        result_state = await graph.invoke(initial_state)

        # Build result payload
        result = SimpleGraphResult(
            final_response=result_state.get("final_response", ""),
            messages=result_state.get("messages", []),
            token_usage=result_state.get("token_usage", {}) or {},
        )

        return SimpleGraphResponse(
            success=True,
            message="SimpleGraph executed successfully",
            data=result,
        )
    except Exception as e:
        # TODO: có thể map sang ErrorResponse chuẩn nếu cần
        return SimpleGraphResponse(
            success=False,
            message=f"Error executing SimpleGraph: {str(e)}",
            data=None,
        )


@router.get("/simple/health")
async def simple_graph_health():
    """
    Health check đơn giản cho SimpleGraph endpoint.
    Không chạy LLM, chỉ xác nhận route hoạt động.
    """
    return {"status": "ok", "graph": "simple"}


