"""
Simple Graph Implementation - Graph đơn giản nhất để minh họa cách build graph.

Graph này sử dụng create_agent với HumanInTheLoopMiddleware để:
- Tự động pause khi cần human approval cho các tool calls
- Hỗ trợ approve/edit/reject cho write_file
- Hỗ trợ approve/reject cho execute_sql (không cho edit)
- Tự động chạy read_data (không cần approval)
"""
from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.base_graph import BaseGraph
from app.schemas.graph.base import BaseGraphState


class SimpleGraph(BaseGraph):
    """
    Simple Graph sử dụng create_agent với HumanInTheLoopMiddleware.
    
    Flow:
        1. Agent nhận user query
        2. Agent quyết định tool nào cần dùng
        3. Nếu tool cần approval (write_file, execute_sql) -> pause và chờ human
        4. Human approve/edit/reject -> agent tiếp tục
        5. Trả về final response
    """

    def __init__(
        self,
        llm=None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        checkpointer: Optional[InMemorySaver] = None,
    ):
        """
        Initialize SimpleGraph với agent và middleware.
        
        Args:
            llm: Pre-initialized LLM instance (optional)
            model_name: Model name (defaults to settings.openai_model)
            temperature: Temperature (defaults to settings.openai_temperature)
            checkpointer: Checkpointer instance (defaults to InMemorySaver)
        """
        # Import tools
        from app.tools import write_file_tool, execute_sql_tool, read_data_tool
        
        # Import create_agent và middleware
        # Thử nhiều cách import vì API có thể thay đổi theo version
        create_agent = None
        HumanInTheLoopMiddleware = None
        
        # Thử import từ langchain.agents (version mới)
        try:
            from langchain.agents import create_agent
            from langchain.agents.middleware import HumanInTheLoopMiddleware
        except ImportError:
            pass
        
        # Thử import từ langgraph.prebuilt
        if create_agent is None:
            try:
                from langgraph.prebuilt import create_agent
            except ImportError:
                pass
        
        # Thử import middleware từ langchain.middleware
        if HumanInTheLoopMiddleware is None:
            try:
                from langchain.middleware import HumanInTheLoopMiddleware
            except ImportError:
                pass
        
        # Nếu vẫn không tìm thấy, raise error
        if create_agent is None:
            raise ImportError(
                "Không tìm thấy create_agent. "
                "Vui lòng kiểm tra version của langchain/langgraph. "
                "Có thể cần: pip install langchain>=0.1.0 langgraph>=0.0.20"
            )
        
        if HumanInTheLoopMiddleware is None:
            raise ImportError(
                "Không tìm thấy HumanInTheLoopMiddleware. "
                "Vui lòng kiểm tra version của langchain/langgraph. "
                "Có thể cần: pip install langchain>=0.1.0"
            )
        
        # Initialize LLM từ BaseGraph
        super().__init__(llm=llm, model_name=model_name, temperature=temperature)
        
        # Sử dụng InMemorySaver thay vì MemorySaver
        self.checkpointer = checkpointer or InMemorySaver()
        
        # Tạo agent với middleware
        self.agent = create_agent(
            model=self.llm,
            tools=[write_file_tool, execute_sql_tool, read_data_tool],
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={
                        "write_file": True,  # All decisions (approve, edit, reject) allowed
                        "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # No editing allowed
                        "read_data": False,  # Safe operation, no approval needed
                    },
                    description_prefix="Tool execution pending approval",
                ),
            ],
            checkpointer=self.checkpointer,
        )
        
        # Graph là agent (để tương thích với BaseGraph interface)
        self.graph = self.agent

    def _build_graph(self):
        """
        Build graph - không cần thiết vì agent đã được tạo trong __init__.
        
        Returns:
            Agent instance (để tương thích với BaseGraph).
            
        Lưu ý:
            BaseGraph.__init__ sẽ gọi _build_graph() trước khi SimpleGraph.__init__
            kịp gán self.agent, nên ở lần gọi đầu tiên sẽ trả về None.
            Sau khi __init__ hoàn tất, self.graph sẽ được gán lại = self.agent.
        """
        return getattr(self, "agent", None)

    async def invoke(
        self,
        state: BaseGraphState,
        thread_id: Optional[str] = None,
        resume_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Invoke agent với state.
        
        Args:
            state: Initial state với query và messages
            thread_id: Thread ID để track conversation (required cho checkpointing)
            resume_value: Human input để resume sau interrupt (optional)
            
        Returns:
            Final state sau khi agent chạy xong hoặc state với __interrupt__ nếu đang chờ human
        """
        if thread_id is None:
            import uuid
            thread_id = str(uuid.uuid4())
        
        # Chuẩn bị input cho agent
        # Agent expects messages format
        messages = state.get("messages", [])
        query = state.get("query", "")
        
        # Thêm user query vào messages nếu chưa có
        if query and (not messages or messages[-1].get("role") != "user"):
            # LangChain mới dùng langchain_core.messages thay vì langchain.schema
            from langchain_core.messages import HumanMessage, AIMessage
            if isinstance(messages, list) and len(messages) > 0:
                # Convert dict messages to LangChain message objects nếu cần
                langchain_messages = []
                for msg in messages:
                    if isinstance(msg, dict):
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        if role == "user":
                            langchain_messages.append(HumanMessage(content=content))
                        elif role == "assistant":
                            langchain_messages.append(AIMessage(content=content))
                    else:
                        langchain_messages.append(msg)
                messages = langchain_messages
            else:
                messages = [HumanMessage(content=query)]
        
        # Config cho agent invocation
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        
        # Nếu có resume_value (human input), thêm vào config
        if resume_value:
            config["configurable"]["resume_value"] = resume_value
        
        try:
            # Invoke agent
            # HumanInTheLoopMiddleware sẽ tự động pause khi cần approval
            result = await self.agent.ainvoke(
                {"messages": messages},
                config=config,
            )
            
            # Kiểm tra xem có đang chờ human input không
            # HumanInTheLoopMiddleware sẽ lưu interrupt state trong checkpoint
            waiting_for_human = False
            file_path = None
            file_content = None
            
            # Kiểm tra checkpoint state để detect interrupt
            try:
                # Lấy checkpoint state hiện tại
                checkpoint = await self.checkpointer.aget(config["configurable"])
                if checkpoint:
                    # Kiểm tra metadata hoặc channel values để tìm interrupt
                    channel_values = checkpoint.get("channel_values", {})
                    # HumanInTheLoopMiddleware có thể lưu interrupt info ở đây
                    if "__interrupt__" in channel_values or checkpoint.get("metadata", {}).get("interrupt"):
                        waiting_for_human = True
            except Exception:
                # Nếu không thể đọc checkpoint, sẽ detect từ messages
                pass
            
            # Convert result về format BaseGraphState
            output_messages = result.get("messages", []) if result else []
            
            # Tìm final response từ last AI message
            final_response = ""
            if output_messages:
                last_message = output_messages[-1]
                if hasattr(last_message, "content"):
                    final_response = last_message.content
                elif isinstance(last_message, dict):
                    final_response = last_message.get("content", "")
            
            # Extract tool calls và file info nếu có
            # Tìm tool calls trong messages để detect write_file hoặc execute_sql interrupt
            for msg in output_messages:
                tool_calls = None
                if hasattr(msg, "tool_calls"):
                    tool_calls = msg.tool_calls
                elif isinstance(msg, dict) and "tool_calls" in msg:
                    tool_calls = msg["tool_calls"]
                
                if tool_calls:
                    for tool_call in tool_calls:
                        # Extract tool name
                        tool_name = None
                        if isinstance(tool_call, dict):
                            tool_name = tool_call.get("name")
                            args = tool_call.get("args", {})
                        else:
                            tool_name = getattr(tool_call, "name", None)
                            args = getattr(tool_call, "args", {})
                        
                        # Check for write_file tool call (needs approval)
                        if tool_name == "write_file":
                            file_path = args.get("file_path") if isinstance(args, dict) else getattr(args, "file_path", None)
                            file_content = args.get("content") if isinstance(args, dict) else getattr(args, "content", None)
                            waiting_for_human = True
                            break
                        # Check for execute_sql tool call (needs approval)
                        elif tool_name == "execute_sql":
                            waiting_for_human = True
                            break
            
            # Convert messages về dict format
            messages_dict = []
            for msg in output_messages:
                if hasattr(msg, "role"):
                    messages_dict.append({
                        "role": msg.role if hasattr(msg, "role") else "assistant",
                        "content": msg.content if hasattr(msg, "content") else str(msg),
                    })
                elif isinstance(msg, dict):
                    messages_dict.append(msg)
                else:
                    messages_dict.append({
                        "role": "assistant",
                        "content": str(msg),
                    })
            
            output_state: Dict[str, Any] = {
                "messages": messages_dict,
                "query": query,
                "final_response": final_response,
                "token_usage": state.get("token_usage", {}),
                "waiting_for_human": waiting_for_human,
                "file_path": file_path,
                "file_content": file_content,
            }
            
            # Nếu đang chờ human, thêm flag đặc biệt
            if waiting_for_human:
                output_state["__interrupt__"] = True
            
            return output_state
            
        except Exception as e:
            # Nếu có lỗi, trả về state với error message
            return {
                "messages": state.get("messages", []),
                "query": query,
                "final_response": f"Lỗi khi thực thi agent: {str(e)}",
                "token_usage": state.get("token_usage", {}),
                "waiting_for_human": False,
                "__error__": str(e),
            }
