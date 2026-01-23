"""
Configuration module - Quản lý settings và environment variables.
Hỗ trợ nhiều API keys và cấu hình database linh hoạt.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Tất cả các API keys và database configs đều có thể được set qua .env file.
    """
    
    # ==================== OpenAI Configuration ====================
    # Primary OpenAI API Key (required when using OpenAI features)
    openai_api_key: Optional[str] = None
    
    # Optional: Secondary OpenAI API Key (for fallback or load balancing)
    openai_api_key_secondary: Optional[str] = None
    
    # OpenAI Model Configuration
    openai_model: str = "gpt-4o-mini"
    openai_model_fallback: Optional[str] = None  # Fallback model nếu primary fail
    openai_temperature: float = 0.7
    openai_max_tokens: Optional[int] = None
    openai_timeout: Optional[int] = 30  # Timeout in seconds
    
    # OpenAI Organization (optional)
    openai_organization: Optional[str] = None
    
    # ==================== MongoDB Configuration ====================
    # MongoDB Connection
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "fastbase"
    
    # MongoDB Connection Options (optional)
    mongodb_max_pool_size: int = 100
    mongodb_min_pool_size: int = 10
    mongodb_connect_timeout: int = 20000  # milliseconds
    
    # ==================== SQL Database Configuration ====================
    # PostgreSQL Configuration
    postgres_host: Optional[str] = None
    postgres_port: Optional[str] = "5432"
    postgres_db: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_ssl_mode: Optional[str] = None  # prefer, require, verify-ca, etc.
    
    # MySQL Configuration
    mysql_host: Optional[str] = None
    mysql_port: Optional[str] = "3306"
    mysql_database: Optional[str] = None
    mysql_user: Optional[str] = None
    mysql_password: Optional[str] = None
    mysql_charset: str = "utf8mb4"
    
    # SQL Database Selection (auto-detect if both configured)
    sql_database_type: Optional[str] = None  # "postgres" or "mysql" (auto-detect if None)
    
    # ==================== External API Keys ====================
    # Các API keys cho external services (optional)
    # Có thể thêm các API keys khác tùy theo nhu cầu
    
    # Example: Vector Database API Keys
    # pinecone_api_key: Optional[str] = None
    # qdrant_api_key: Optional[str] = None
    
    # Example: Other AI Services
    # anthropic_api_key: Optional[str] = None
    # cohere_api_key: Optional[str] = None
    
    # Example: Embedding Services
    # openai_embedding_model: str = "text-embedding-3-small"
    
    # ==================== Application Configuration ====================
    app_name: str = "FastBase AI"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Configuration
    api_prefix: str = "/api/v1"
    api_title: Optional[str] = None  # Defaults to app_name
    api_description: Optional[str] = None
    
    # CORS Configuration
    cors_origins: str = "*"  # Comma-separated list or "*" for all
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"  # Comma-separated list or "*" for all
    cors_allow_headers: str = "*"  # Comma-separated list or "*" for all
    
    # ==================== Logging Configuration ====================
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None  # Optional log file path
    
    # ==================== Graph Configuration ====================
    graph_max_iterations: int = 50
    graph_timeout: Optional[int] = None
    
    # Retriever Configuration
    retriever_top_k: int = 5  # Number of documents to retrieve
    retriever_score_threshold: Optional[float] = None
    
    # ==================== Security Configuration ====================
    # API Key for protecting endpoints (optional)
    api_secret_key: Optional[str] = None
    
    # Rate Limiting (optional)
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow extra fields for flexibility
        extra = "ignore"
    
    def get_openai_api_key(self, use_secondary: bool = False) -> str:
        """
        Get OpenAI API key (primary or secondary).
        
        Args:
            use_secondary: If True, return secondary key if available
            
        Returns:
            API key string
            
        Raises:
            ValueError: If no API key is configured
        """
        if use_secondary and self.openai_api_key_secondary:
            return self.openai_api_key_secondary
        
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key is required but not configured. "
                "Please set OPENAI_API_KEY environment variable or add it to your .env file. "
                "See env.example for configuration details."
            )
        
        return self.openai_api_key
    
    def get_sql_database_type(self) -> Optional[str]:
        """
        Auto-detect SQL database type from configuration.
        
        Returns:
            "postgres", "mysql", or None if not configured
        """
        if self.sql_database_type:
            return self.sql_database_type.lower()
        
        # Auto-detect
        if self.postgres_host and self.postgres_db:
            return "postgres"
        if self.mysql_host and self.mysql_database:
            return "mysql"
        
        return None


settings = Settings()

