"""
Simple Graph Implementation - Graph đơn giản nhất để minh họa cách build graph.

Graph này có flow đơn giản:
    entry -> generate -> END
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage

from app.graph.base_graph import BaseGraph
from app.schemas.graph.base import BaseGraphState


class SimpleGraph(BaseGraph):
    """
    Simple graph implementation - Graph đơn giản nhất.
    
    Flow:
        entry -> generate -> END
    
    Graph này chỉ có 1 node để generate response từ LLM.
    """
    
    def _build_graph(self) -> StateGraph:
        """
        Build graph workflow đơn giản.
        
        Returns:
            Compiled StateGraph instance
        """
        # Tạo StateGraph với BaseGraphState
        workflow = StateGraph(BaseGraphState)
        
        # Thêm node duy nhất: generate
        workflow.add_node("generate", self._generate_node)
        
        # Set entry point
        workflow.set_entry_point("generate")
        
        # Kết nối generate -> END
        workflow.add_edge("generate", END)
        
        # Compile và return
        return workflow.compile()
    
    async def _generate_node(self, state: BaseGraphState) -> Dict[str, Any]:
        """
        Generate node - Gọi LLM để generate response.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state với final_response
        """
        query = state.get("query", "")
        
        # Tạo message từ query
        messages = [HumanMessage(content=query)]
        
        # Gọi LLM
        response = await self.llm.ainvoke(messages)
        
        # Lấy response content
        final_response = response.content if hasattr(response, 'content') else str(response)
        
        # Update messages
        updated_messages = state.get("messages", [])
        updated_messages.append({"role": "user", "content": query})
        updated_messages.append({"role": "assistant", "content": final_response})
        
        # Return updated state
        return {
            "messages": updated_messages,
            "final_response": final_response,
            "token_usage": {
                "prompt_tokens": getattr(response, 'response_metadata', {}).get('token_usage', {}).get('prompt_tokens', 0),
                "completion_tokens": getattr(response, 'response_metadata', {}).get('token_usage', {}).get('completion_tokens', 0),
                "total_tokens": getattr(response, 'response_metadata', {}).get('token_usage', {}).get('total_tokens', 0),
            }
        }
    
    async def invoke(self, state: BaseGraphState) -> Dict[str, Any]:
        """
        Invoke graph với state.
        
        Args:
            state: Initial state với query
            
        Returns:
            Final state sau khi graph execution
        """
        return await self.graph.ainvoke(state)

