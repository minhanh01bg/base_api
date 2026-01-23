"""
Graph module - LangGraph definitions và base classes cho AI text generation.
"""
from .base_graph import BaseGraph
from .simple_graph import SimpleGraph
from app.schemas.graph.base import BaseGraphState

# Try to import Graph if exists (optional)
try:
    from .graph import Graph, GraphState
    __all__ = [
        "BaseGraph",
        "BaseGraphState",
        "SimpleGraph",
        "Graph",
        "GraphState",
    ]
except ImportError:
    __all__ = [
        "BaseGraph",
        "BaseGraphState",
        "SimpleGraph",
    ]

