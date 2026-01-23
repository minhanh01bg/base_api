"""
Example Service Implementation - Mẫu cách implement service sử dụng BaseService.
"""
from typing import Dict, Any, Optional
from app.services.base_service import BaseService
from app.graph.base_graph import BaseGraph


class ExampleGraphService(BaseService):
    """
    Example service cho graph operations.
    
    Service này wrap graph và cung cấp business logic layer.
    """
    
    def __init__(self, graph: BaseGraph):
        """
        Initialize service với graph dependency.
        
        Args:
            graph: Graph instance để sử dụng
        """
        super().__init__()
        self.graph = graph
    
    def _validate_input(self, **kwargs) -> None:
        """
        Validate input parameters.
        
        Args:
            **kwargs: Input parameters
            
        Raises:
            ValueError: If validation fails
        """
        query = kwargs.get("query")
        if not query:
            raise ValueError("Query is required")
        if not isinstance(query, str):
            raise ValueError("Query must be a string")
        if len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process user query qua graph.
        
        Args:
            query: User query string
            session_id: Optional session ID for logging
            
        Returns:
            Response dictionary với success status và data
        """
        try:
            # Validate input
            self._validate_input(query=query)
            
            # Create initial state
            initial_state = {
                "messages": [],
                "query": query,
                "final_response": "",
                "token_usage": {},
            }
            
            # Invoke graph
            result = await self.graph.invoke(initial_state)
            
            # Log if session_id provided
            if session_id:
                self.logger.info(
                    f"Processed query for session {session_id}",
                    extra={"query": query[:100], "session_id": session_id}
                )
            
            # Return success response
            return self._create_success_response(
                data={
                    "response": result.get("final_response", ""),
                    "state": result,
                },
                message="Query processed successfully"
            )
        except ValueError as e:
            # Validation error
            return self._handle_error(e, context={"query": query})
        except Exception as e:
            # Other errors
            return self._handle_error(
                e,
                context={
                    "query": query,
                    "session_id": session_id,
                }
            )

