"""
Main application entry point cho base structure.
FastAPI application với base structure.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.exceptions import BaseAppException
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
# TẠM THỜI ẨN - Chỉ sử dụng MongoDB hiện tại
# from app.core.sql_database import init_sql_connector, get_sql_connector

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title or settings.app_name,
    version=settings.app_version,
    description=settings.api_description,
    debug=settings.debug
)

# CORS middleware - configurable từ settings
cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
cors_methods = settings.cors_allow_methods.split(",") if settings.cors_allow_methods != "*" else ["*"]
cors_headers = settings.cors_allow_headers.split(",") if settings.cors_allow_headers != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=[method.strip() for method in cors_methods],
    allow_headers=[header.strip() for header in cors_headers],
)

# Register error handlers
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def startup_event():
    """
    Initialize connections và resources on startup.
    
    - MongoDB connection
    - SQL database connection (PostgreSQL/MySQL)
    - Graph initialization (nếu có)
    """
    # Kết nối MongoDB
    logger.info("=" * 60)
    logger.info("Đang kết nối đến MongoDB...")
    try:
        await connect_to_mongo()
        logger.info("✓ MongoDB connected successfully")
    except Exception as e:
        logger.error("=" * 60)
        logger.error("✗ LỖI KẾT NỐI MONGODB!")
        logger.error(f"  - Error: {str(e)}")
        logger.error("=" * 60)
        raise
    
    # TẠM THỜI ẨN - Chỉ sử dụng MongoDB hiện tại
    # Kết nối SQL Database (PostgreSQL/MySQL)
    # logger.info("=" * 60)
    # logger.info("Đang kết nối đến SQL database...")
    # try:
    #     # Auto-detect database type từ environment
    #     sql_connector = init_sql_connector()
    #     if sql_connector is None:
    #         logger.warning(
    #             "⚠ Không thể kết nối SQL database: "
    #             "Không tìm thấy cấu hình trong environment variables"
    #         )
    #         logger.warning(
    #             "   Vui lòng kiểm tra các biến: "
    #             "POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD "
    #             "hoặc MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD"
    #         )
    #     else:
    #         # Kiểm tra kết nối
    #         if sql_connector.test_connection():
    #             tables = sql_connector.get_tables()
    #             table_count = len(tables) if tables else 0
    #             logger.info("=" * 60)
    #             logger.info(f"✓ {sql_connector.db_type.upper()} DATABASE CONNECTED SUCCESSFULLY!")
    #             logger.info(f"  - Host: {sql_connector.host}:{sql_connector.port}")
    #             logger.info(f"  - Database: {sql_connector.database}")
    #             logger.info(f"  - User: {sql_connector.user}")
    #             logger.info(f"  - Số bảng: {table_count}")
    #             if table_count > 0:
    #                 logger.info(
    #                     f"  - Danh sách bảng: "
    #                     f"{', '.join(tables[:10])}{'...' if table_count > 10 else ''}"
    #                 )
    #             logger.info("=" * 60)
    #         else:
    #             logger.error("✗ SQL database connection test failed")
    # except Exception as e:
    #     logger.error("=" * 60)
    #     logger.error("✗ LỖI KẾT NỐI SQL DATABASE!")
    #     logger.error(f"  - Error: {str(e)}")
    #     logger.error("=" * 60)
    #     # Không raise để app vẫn có thể chạy nếu không cần SQL
    
    # TODO: Initialize graph và retriever nếu cần
    # Ví dụ:
    # from base.graph import Graph
    # from base.graph.data_retriever import DataRetriever
    # 
    # logger.info("=" * 60)
    # logger.info("Đang khởi tạo Graph...")
    # try:
    #     data_retriever = await DataRetriever.create_with_embeddings()
    #     graph = Graph(data_retriever=data_retriever)
    #     app.state.graph = graph
    #     logger.info("✓ Graph initialized successfully")
    # except Exception as e:
    #     logger.warning(f"⚠ Không thể khởi tạo Graph: {str(e)}")
    
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown."""
    await close_mongo_connection()
    logger.info("Application shut down successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "status": "running",
        "structure": "base"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status của application và databases
    """
    health_status = {
        "status": "healthy",
        "mongodb": "unknown",
        "sql_database": "unknown",
    }
    
    # Check MongoDB
    try:
        from app.core.database import get_database
        db = get_database()
        if db:
            # Test connection
            await db.client.admin.command('ping')
            health_status["mongodb"] = "connected"
        else:
            health_status["mongodb"] = "not_connected"
    except Exception as e:
        health_status["mongodb"] = f"error: {str(e)}"
    
    # TẠM THỜI ẨN - Chỉ sử dụng MongoDB hiện tại
    # Check SQL Database
    # try:
    #     sql_connector = get_sql_connector()
    #     if sql_connector and sql_connector.test_connection():
    #         health_status["sql_database"] = "connected"
    #     else:
    #         health_status["sql_database"] = "not_configured"
    # except Exception as e:
    #     health_status["sql_database"] = f"error: {str(e)}"
    health_status["sql_database"] = "disabled"
    
    # Overall status
    if health_status["mongodb"] != "connected":
        health_status["status"] = "degraded"
    
    return health_status


# Include API routers (không bọc try/except để thấy lỗi rõ ràng khi import fail)
from app.api.routes import api_router
app.include_router(api_router, prefix=settings.api_prefix)
logger.info("API routes loaded successfully")

