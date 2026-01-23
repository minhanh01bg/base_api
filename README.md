# Base Structure - AI Text Generation Framework

Cấu trúc chuẩn dành riêng cho viết Graph và Service cho AI Text Generation, được xây dựng dựa trên `app` hiện tại với các cải tiến và chuẩn hóa.

## 📁 Cấu trúc thư mục

```
base/
├── __init__.py                 # Module initialization
├── main.py                     # FastAPI application entry point
├── README.md                   # Documentation này
│
├── api/                        # API routes và endpoints
│   ├── __init__.py
│   └── routes/                 # API route definitions
│       ├── __init__.py
│       └── example.py          # Example route
│
├── core/                       # Core utilities và configuration
│   ├── __init__.py
│   ├── config.py              # Settings và environment variables
│   ├── database.py            # MongoDB connection management
│   ├── sql_database.py        # SQL database connector (PostgreSQL/MySQL)
│   └── dependencies.py        # Dependency injection setup
│
├── graph/                      # LangGraph definitions
│   ├── __init__.py
│   ├── base_graph.py          # Abstract base classes cho graphs
│   └── graph.py               # Graph implementations (example)
│
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── base_service.py        # Abstract base class cho services
│   └── graph_service.py       # Graph service implementations (example)
│
├── models/                     # Domain models
│   └── __init__.py
│
├── schemas/                    # Pydantic schemas cho API
│   └── __init__.py
│
└── utils/                      # Helper utilities
    ├── __init__.py
    ├── llm_utils.py           # LLM helper functions
    └── retriever_utils.py     # Retriever helper functions
```

## 🎯 Design Principles

### 1. Separation of Concerns
- **Graph**: Chỉ chứa graph definitions và nodes
- **Services**: Business logic và orchestration
- **Core**: Configuration, database, utilities
- **Models**: Domain models (Pydantic)
- **Schemas**: API request/response schemas

### 2. Dependency Injection
- Services nhận dependencies qua constructor
- Không hardcode dependencies trong business logic
- Dễ dàng test và mock

### 3. Base Classes
- `BaseGraph`: Abstract base cho tất cả graphs
- `BaseService`: Abstract base cho tất cả services
- Cung cấp common patterns và utilities

### 4. Error Handling
- Consistent error handling patterns
- Proper logging và error messages
- Graceful degradation

## 📝 Usage Examples

### 1. Tạo Graph mới

```python
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from base.graph.base_graph import BaseGraph, BaseGraphState

class MyGraphState(BaseGraphState):
    """Extended state cho graph của bạn."""
    custom_field: str

class MyGraph(BaseGraph):
    """Graph implementation của bạn."""
    
    def _build_graph(self):
        workflow = StateGraph(MyGraphState)
        
        # Add nodes
        workflow.add_node("process", self._process_node)
        
        # Set entry point
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        return workflow.compile()
    
    async def _process_node(self, state: MyGraphState) -> Dict[str, Any]:
        """Process node implementation."""
        # Your logic here
        return {"final_response": "Processed"}
    
    async def invoke(self, state: MyGraphState) -> Dict[str, Any]:
        """Invoke graph."""
        return await self.graph.ainvoke(state)
```

### 2. Tạo Service mới

```python
from base.services.base_service import BaseService
from base.graph import Graph

class MyGraphService(BaseService):
    """Service cho graph operations."""
    
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query."""
        try:
            # Validate input
            self._validate_input(query=query)
            
            # Create initial state
            state = {
                "messages": [],
                "query": query,
                "final_response": "",
                "token_usage": {},
            }
            
            # Invoke graph
            result = await self.graph.invoke(state)
            
            # Return success response
            return self._create_success_response(
                data=result,
                message="Query processed successfully"
            )
        except Exception as e:
            return self._handle_error(e, context={"query": query})
```

### 3. Sử dụng Utilities

```python
from base.utils.llm_utils import create_llm, create_messages, format_token_usage
from base.utils.retriever_utils import format_retrieved_docs

# Create LLM
llm = create_llm(model_name="gpt-4o-mini", temperature=0.7)

# Create messages
messages = create_messages(
    system_prompt="You are a helpful assistant.",
    user_message="Hello!"
)

# Format retrieved docs
context = format_retrieved_docs(retrieved_docs, max_length=1000)
```

### 4. Dependency Injection

```python
from base.core.dependencies import get_settings, get_db, get_sql_db
from base.services.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.db = get_db()
        self.sql_db = get_sql_db()
```

## 🚀 Running the Application

### Cách 1: Sử dụng uvicorn trực tiếp

```bash
# Từ thư mục fast-base
uvicorn base.main:app --reload --host 0.0.0.0 --port 8000
```

### Cách 2: Sử dụng Python module

```bash
# Từ thư mục fast-base
python -m uvicorn base.main:app --reload
```

### Cách 3: Tạo script riêng

Tạo file `run.py` trong thư mục root:

```python
import uvicorn
from base.main import app

if __name__ == "__main__":
    uvicorn.run(
        "base.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

Sau đó chạy:
```bash
python run.py
```

### Kiểm tra ứng dụng

- Root endpoint: http://localhost:8000/
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

Cấu hình được quản lý qua environment variables (`.env` file).

### Quick Setup

```bash
# Tạo .env file từ template
python base/create_env.py

# Hoặc copy thủ công
cp base/env.example .env
```

### Required Configuration

Cập nhật các giá trị bắt buộc trong `.env`:

```env
# OpenAI (Required)
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB (Required)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=fastbase
```

### Optional Configuration

Xem `base/CONFIG_GUIDE.md` để biết chi tiết về:
- Multiple OpenAI API keys (primary/secondary)
- SQL Database (PostgreSQL/MySQL)
- External API keys
- CORS, Security, Rate Limiting
- Logging và Graph configuration

### Configuration Files

- `base/env.example` - Template với tất cả options
- `base/CONFIG_GUIDE.md` - Hướng dẫn chi tiết
- `base/create_env.py` - Script helper để tạo .env

## 🚀 Migration từ app/

Khi migrate từ `app/` sang `base/`:

1. **Graph**: Kế thừa từ `BaseGraph` thay vì tự implement
2. **Services**: Kế thừa từ `BaseService` và sử dụng dependency injection
3. **Config**: Sử dụng `base.core.config.settings`
4. **Database**: Sử dụng `base.core.database` và `base.core.sql_database`
5. **Utils**: Sử dụng utilities từ `base.utils`

## 📋 Best Practices

1. **Graph Nodes**: Mỗi node nên có single responsibility
2. **Service Methods**: Methods nên có clear input/output
3. **Error Handling**: Luôn handle errors và return consistent responses
4. **Logging**: Sử dụng structured logging với context
5. **Testing**: Dễ dàng test nhờ dependency injection

## 🔍 So sánh với app/

### Cải tiến chính:

1. **Base Classes**: Thêm abstract base classes cho consistency
2. **Dependency Injection**: Proper DI setup
3. **Utilities**: Tách utilities thành modules riêng
4. **Error Handling**: Standardized error handling
5. **Documentation**: Comprehensive documentation

### Điều chỉnh:

1. **Config**: Thêm các config options cho graph (max_iterations, timeout)
2. **Database**: Improved error handling và validation
3. **Services**: Base class với common patterns
4. **Graph**: Base class với common LLM setup

## 📚 Next Steps

1. **Setup environment**: Tạo `.env` file với các biến cần thiết
2. **Implement specific graphs**: Tạo graph implementations trong `base/graph/`
3. **Implement specific services**: Tạo service implementations trong `base/services/`
4. **Add API routes**: Tạo API routes trong `base/api/routes/`
5. **Add domain models**: Thêm models vào `base/models/`
6. **Add API schemas**: Thêm schemas vào `base/schemas/`
7. **Add tests**: Tạo tests cho từng module
8. **Run application**: Chạy `uvicorn base.main:app --reload`

## 🤝 Contributing

Khi thêm code mới vào base:

1. Follow existing patterns
2. Use base classes khi có thể
3. Add proper error handling
4. Add logging
5. Update documentation

