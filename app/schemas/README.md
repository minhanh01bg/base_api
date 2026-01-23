# Schemas Organization Guide

## 📁 Cấu trúc Schemas

```
schemas/
├── __init__.py
├── api/                    # API Schemas (Pydantic BaseModel)
│   ├── __init__.py
│   └── example.py          # Example API schemas
└── graph/                  # Graph State Schemas (TypedDict)
    ├── __init__.py
    └── base.py             # Base graph state schemas
```

## 🎯 Sự khác biệt giữa các loại Schemas

### 1. **API Schemas** (`schemas/api/`)

**Mục đích**: Định nghĩa request/response cho FastAPI endpoints

**Đặc điểm**:
- Sử dụng **Pydantic BaseModel**
- Tự động validation khi nhận request
- Tự động serialization khi trả response
- Tự động generate OpenAPI/Swagger documentation
- Immutable (không thể thay đổi sau khi tạo)

**Ví dụ sử dụng**:
```python
from app.schemas.api.example import ExampleRequest, ExampleResponse

@router.post("/example", response_model=ExampleResponse)
async def example_endpoint(request: ExampleRequest):
    # request.message đã được validate tự động
    return ExampleResponse(success=True, message="OK")
```

### 2. **Graph State Schemas** (`schemas/graph/`)

**Mục đích**: Định nghĩa state structure cho LangGraph workflows

**Đặc điểm**:
- Sử dụng **TypedDict** (yêu cầu của LangGraph)
- State có thể được mutate trong graph execution
- Không có validation tự động (graph tự quản lý)
- Type-safe nhưng flexible
- Có thể có optional fields với `total=False`

**Ví dụ sử dụng**:
```python
from app.schemas.graph.base import BaseGraphState

class MyGraphState(BaseGraphState):
    additional_field: str

def my_node(state: MyGraphState) -> MyGraphState:
    # State có thể được modify
    state["final_response"] = "Updated response"
    return state
```

### 3. **Domain Models** (`models/`)

**Mục đích**: Đại diện cho business entities với business logic

**Đặc điểm**:
- Có thể là plain Python classes, dataclasses, hoặc Pydantic models
- Có thể chứa methods và business logic
- Đại diện cho entities trong domain (User, Conversation, Document, etc.)
- Có thể có relationships với các models khác

**Ví dụ sử dụng**:
```python
from app.models.example import Conversation

conversation = Conversation(
    id="123",
    user_id="user_1",
    messages=[],
    created_at=datetime.now()
)
conversation.add_message({"role": "user", "content": "Hello"})
```

## 📋 Quy tắc sử dụng

### ✅ Khi nào dùng API Schemas?
- Định nghĩa request body cho API endpoints
- Định nghĩa response format cho API endpoints
- Cần validation tự động
- Cần generate API documentation

### ✅ Khi nào dùng Graph State Schemas?
- Định nghĩa state cho LangGraph workflows
- State cần được mutate qua các nodes
- Cần type safety cho graph execution

### ✅ Khi nào dùng Domain Models?
- Đại diện cho business entities
- Cần business logic và methods
- Cần lưu vào database
- Cần relationships giữa các entities

## 🔄 Mapping giữa các loại

```
API Request → Domain Model → Graph State → Domain Model → API Response
   (Pydantic)    (Business)    (TypedDict)    (Business)     (Pydantic)
```

**Ví dụ flow**:
1. API nhận `ExampleRequest` (Pydantic)
2. Convert sang `Conversation` model (Domain)
3. Pass vào Graph với `BaseGraphState` (TypedDict)
4. Graph xử lý và update state
5. Convert kết quả về `Conversation` model
6. Return `ExampleResponse` (Pydantic)

## 📝 Best Practices

1. **Tách biệt rõ ràng**: Không mix API schemas với Graph schemas
2. **Naming convention**: 
   - API: `*Request`, `*Response`
   - Graph: `*State`, `*GraphState`
   - Models: Tên entity (noun)
3. **Reusability**: Có thể tái sử dụng domain models trong cả API và Graph
4. **Validation**: API schemas validate input, Graph schemas chỉ type-check
5. **Documentation**: Thêm docstrings cho tất cả schemas

