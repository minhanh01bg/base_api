"""
Simple Graph Example - Ví dụ sử dụng SimpleGraph.

Cách chạy:
    python -m app.examples.simple_graph_example
"""
import asyncio
from app.graph.simple_graph import SimpleGraph
from app.schemas.graph.base import BaseGraphState


async def main():
    """Example usage của SimpleGraph."""
    print("=" * 60)
    print("Simple Graph Example")
    print("=" * 60)
    
    # Tạo graph instance
    graph = SimpleGraph()
    
    # Tạo initial state
    initial_state: BaseGraphState = {
        "messages": [],
        "query": "Xin chào! Bạn có thể giới thiệu về Python không?",
        "final_response": "",
        "token_usage": {},
    }
    
    print(f"\n📝 Query: {initial_state['query']}\n")
    print("🔄 Đang chạy graph...\n")
    
    # Invoke graph
    result = await graph.invoke(initial_state)
    
    # Hiển thị kết quả
    print("=" * 60)
    print("📤 Kết quả:")
    print("=" * 60)
    print(f"\n💬 Response:\n{result.get('final_response', '')}\n")
    
    # Hiển thị token usage
    token_usage = result.get('token_usage', {})
    if token_usage:
        print("📊 Token Usage:")
        print(f"  - Prompt tokens: {token_usage.get('prompt_tokens', 0)}")
        print(f"  - Completion tokens: {token_usage.get('completion_tokens', 0)}")
        print(f"  - Total tokens: {token_usage.get('total_tokens', 0)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

