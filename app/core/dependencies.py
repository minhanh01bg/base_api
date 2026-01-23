"""
Dependencies module - Dependency injection setup cho base structure.
"""
from typing import Optional
from functools import lru_cache

from .config import settings
from .database import get_database
from .sql_database import get_sql_connector


@lru_cache()
def get_settings():
    """
    Get settings instance (cached).
    
    Returns:
        Settings instance
    """
    return settings


def get_db():
    """
    Get database instance (dependency injection).
    
    Returns:
        Database instance
        
    Raises:
        RuntimeError: If database is not connected
    """
    return get_database()


def get_sql_db():
    """
    Get SQL database connector (dependency injection).
    
    Returns:
        SQLConnector instance or None
    """
    return get_sql_connector()

