"""
Pytest configuration và fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app


@pytest.fixture
def client():
    """Test client cho FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings."""
    with patch("app.core.config.settings") as mock:
        mock.app_name = "Test App"
        mock.app_version = "1.0.0"
        mock.debug = True
        mock.openai_api_key = "test-key"
        mock.mongodb_url = "mongodb://localhost:27017"
        mock.mongodb_db_name = "test_db"
        yield mock


@pytest.fixture
def mock_database():
    """Mock MongoDB database."""
    with patch("app.core.database.get_database") as mock:
        mock_db = Mock()
        mock_db.client.admin.command.return_value = {"ok": 1}
        mock.return_value = mock_db
        yield mock_db

