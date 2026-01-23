"""
Example Graph Implementation - Mẫu cách implement graph sử dụng BaseGraph.
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from app.graph.base_graph import BaseGraph
from app.schemas.graph.base import BaseGraphState


class ExampleGraphState(BaseGraphState):
    """
    Extended state cho example graph.
    
    Kế thừa từ BaseGraphState và thêm các fields riêng.
    """
    intent: str
    processed_data: Dict[str, Any]


class ExampleGraph(BaseGraph):
    """
    Example graph implementation.
    
    Flow:
        entry -> process -> format -> END
    """
    
    def _build_graph(self):
        """Build graph workflow."""
        workflow = StateGraph(ExampleGraphState)
        
        # Add nodes
        workflow.add_node("process", self._process_node)
        workflow.add_node("format", self._format_node)
        
        # Set entry point
        workflow.set_entry_point("process")
        
        # Add edges
        workflow.add_edge("process", "format")
        workflow.add_edge("format", END)
        
        return workflow.compile()
    
    async def _process_node(
        self, state: ExampleGraphState
    ) -> Dict[str, Any]:
        """Process node - xử lý query."""
        query = state.get("query", "")
        
        # Example: Simple processing
        processed_data = {
            "query": query,
            "length": len(query),
            "words": query.split(),
        }
        
        return {
            "intent": "example",
            "processed_data": processed_data,
        }
    
    async def _format_node(
        self, state: ExampleGraphState
    ) -> Dict[str, Any]:
        """Format node - format response."""
        processed_data = state.get("processed_data", {})
        query = state.get("query", "")
        
        # Example: Format response
        response = (
            f"Processed query: {query}\n"
            f"Length: {processed_data.get('length', 0)}\n"
            f"Words: {len(processed_data.get('words', []))}"
        )
        
        return {"final_response": response}
    
    async def invoke(self, state: ExampleGraphState) -> Dict[str, Any]:
        """Invoke graph với state."""
        return await self.graph.ainvoke(state)

