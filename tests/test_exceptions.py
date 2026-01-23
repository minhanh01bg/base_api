"""
Tests cho custom exceptions.
"""
import pytest
from app.core.exceptions import (
    BaseAppException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    GraphExecutionError,
    LLMError,
    ConfigurationError,
)


def test_base_app_exception():
    """Test BaseAppException."""
    exc = BaseAppException("Test error", status_code=400)
    assert str(exc) == "Test error"
    assert exc.status_code == 400
    assert exc.details == {}


def test_validation_error():
    """Test ValidationError."""
    exc = ValidationError("Invalid input", details={"field": "email"})
    assert exc.status_code == 400
    assert exc.details == {"field": "email"}


def test_not_found_error():
    """Test NotFoundError."""
    exc = NotFoundError()
    assert exc.status_code == 404
    assert exc.message == "Resource not found"


def test_database_error():
    """Test DatabaseError."""
    exc = DatabaseError("Connection failed")
    assert exc.status_code == 500


def test_graph_execution_error():
    """Test GraphExecutionError."""
    exc = GraphExecutionError("Graph failed")
    assert exc.status_code == 500


def test_llm_error():
    """Test LLMError."""
    exc = LLMError("API error")
    assert exc.status_code == 502


def test_configuration_error():
    """Test ConfigurationError."""
    exc = ConfigurationError("Config missing")
    assert exc.status_code == 500

