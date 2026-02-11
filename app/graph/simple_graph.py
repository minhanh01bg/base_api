"""
Simple Graph Implementation - Graph đơn giản minh họa human-in-the-loop.

Thiết kế lại theo hướng:
- Không dùng create_agent / HumanInTheLoopMiddleware (tránh lỗi get_config).
- Vẫn giữ human-in-the-loop ở mức ứng dụng:
  - Bước 1: LLM phân loại intent (question / request).
  - Bước 2: Nếu request (ghi file), LLM tự đề xuất file_name + file_content.
  - Bước 3: Trả về cho UI để human review (pause) với cờ __interrupt__.
  - Bước 4: /continue nhận quyết định của human (approve / reject / edit) rồi mới ghi file.
"""
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END

from app.graph.base_graph import BaseGraph
from app.schemas.graph.base import BaseGraphState, IntentClassification, FileInfo
from app.prompts.intent_classification import INTENT_CLASSIFICATION_PROMPT
from app.prompts.extract_file_info import EXTRACT_FILE_INFO_PROMPT

# In-memory store để giữ thông tin request theo thread_id giữa /start và /continue.
# Chỉ dùng cho demo/dev; production nên dùng storage bền vững (DB, Redis, ...).
_PENDING_FILE_REQUESTS: Dict[str, Dict[str, Any]] = {}


class SimpleGraph(BaseGraph):
    """
    SimpleGraph với human-in-the-loop được implement ở tầng ứng dụng,
    không phụ thuộc create_agent hay LangChain middleware.

    Flow:
        - question intent: trả lời trực tiếp, không cần human.
        - request intent (ghi file):
            1) LLM tạo file_name + file_content (chưa ghi).
            2) Trả về UI với __interrupt__ và waiting_for_human = True.
            3) Human gửi quyết định qua /continue:
               - "đồng ý"/"approve"  -> ghi file như đề xuất.
               - "từ chối"/"reject"  -> không ghi file.
               - Text khác           -> coi như nội dung file đã được human edit, ghi file với nội dung đó.
    """

    def _build_graph(self) -> StateGraph:
        """
        Ở bản thiết kế này, ta không dùng LangGraph cho logic chính,
        nhưng vẫn trả về một graph tối thiểu để BaseGraph không lỗi.
        """
        workflow = StateGraph(BaseGraphState)

        async def _noop(state: BaseGraphState) -> Dict[str, Any]:
            return state

        workflow.add_node("noop", _noop)
        workflow.set_entry_point("noop")
        workflow.add_edge("noop", END)
        return workflow.compile()

    async def _classify_intent(self, query: str) -> str:
        """
        Dùng LLM để phân loại intent (question / request).
        """
        structured_llm = self.llm.with_structured_output(IntentClassification)
        prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)
        result: IntentClassification = await structured_llm.ainvoke(prompt)
        intent = result.intent.strip().lower()
        if intent not in ("question", "request"):
            # Fail-safe: nếu model trả linh tinh, coi như question
            intent = "question"
        return intent

    async def _propose_file(self, query: str) -> FileInfo:
        """
        Dùng LLM để đề xuất file_name + file_content từ user query.
        """
        structured_llm = self.llm.with_structured_output(FileInfo)
        prompt = EXTRACT_FILE_INFO_PROMPT.format(query=query)
        result: FileInfo = await structured_llm.ainvoke(prompt)
        return result

    async def _answer_question(self, query: str, messages: Optional[list] = None) -> str:
        """
        Trả lời câu hỏi bình thường (không có side-effect).
        """
        from langchain_core.messages import HumanMessage

        history = []
        if messages:
            # Giữ mọi thứ đơn giản: chỉ dùng query hiện tại làm input chính
            # Có thể mở rộng để convert full history nếu cần.
            pass

        response = await self.llm.ainvoke([HumanMessage(content=query)])
        # ChatOpenAI trả về message có content
        return getattr(response, "content", str(response))

    async def invoke(
        self,
        state: BaseGraphState,
        thread_id: Optional[str] = None,
        resume_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Thực thi SimpleGraph với human-in-the-loop ở tầng ứng dụng.

        Args:
            state: Initial state (ít nhất phải có "query" cho lần đầu).
            thread_id: Thread ID để gắn với pending request (bắt buộc khi có human-in-the-loop).
            resume_value: Human input khi resume sau interrupt (approve/reject/edit).
        """
        # Chuẩn hóa input
        query = state.get("query", "") or ""
        messages = state.get("messages", []) or []
        token_usage = state.get("token_usage", {}) or {}

        # =========================
        # 2. Nhánh resume (sau interrupt)
        # =========================
        if resume_value is not None:
            # Cần có thread_id để map về pending request
            if not thread_id:
                return {
                    "messages": messages,
                    "query": query,
                    "final_response": "Không có thread_id để resume human-in-the-loop.",
                    "token_usage": token_usage,
                    "waiting_for_human": False,
                }

            pending = _PENDING_FILE_REQUESTS.get(thread_id)
            if not pending:
                return {
                    "messages": messages,
                    "query": query,
                    "final_response": "Không tìm thấy yêu cầu đang chờ phê duyệt cho thread này.",
                    "token_usage": token_usage,
                    "waiting_for_human": False,
                }

            file_path = pending["file_path"]
            original_content = pending["file_content"]

            decision = str(resume_value).strip().lower()

            # Import tool ghi file
            from app.tools import write_file_tool

            # 3 case:
            # - approve: đồng ý / approve
            # - reject : từ chối / reject
            # - edit   : mọi text khác => coi như nội dung file mới
            if "đồng ý" in decision or "approve" in decision:
                # Ghi file với nội dung gốc do LLM đề xuất
                result_msg = write_file_tool.invoke(
                    {"file_path": file_path, "content": original_content}
                )
                _PENDING_FILE_REQUESTS.pop(thread_id, None)

                final_response = (
                    f"✅ Đã ghi file theo đề xuất ban đầu.\n\n"
                    f"File: {file_path}\n\nKết quả: {result_msg}"
                )

                return {
                    "messages": messages + [{"role": "assistant", "content": final_response}],
                    "query": query,
                    "final_response": final_response,
                    "token_usage": token_usage,
                    "intent": "request",
                    "file_path": file_path,
                    "file_content": None,  # Không trả về content sau khi đã ghi
                    "waiting_for_human": False,
                }

            if "từ chối" in decision or "reject" in decision:
                _PENDING_FILE_REQUESTS.pop(thread_id, None)
                final_response = (
                    f"❌ Bạn đã từ chối yêu cầu ghi file.\n"
                    f"File đề xuất: {file_path} (KHÔNG được ghi)."
                )
                return {
                    "messages": messages + [{"role": "assistant", "content": final_response}],
                    "query": query,
                    "final_response": final_response,
                    "token_usage": token_usage,
                    "intent": "request",
                    "file_path": file_path,
                    "file_content": None,
                    "waiting_for_human": False,
                }

            # Mọi trường hợp khác: coi như nội dung file đã được human edit
            edited_content = str(resume_value)
            result_msg = write_file_tool.invoke(
                {"file_path": file_path, "content": edited_content}
            )
            _PENDING_FILE_REQUESTS.pop(thread_id, None)

            final_response = (
                f"✏️ Đã ghi file với nội dung bạn cung cấp.\n\n"
                f"File: {file_path}\n\nKết quả: {result_msg}"
            )
            return {
                "messages": messages + [{"role": "assistant", "content": final_response}],
                "query": query,
                "final_response": final_response,
                "token_usage": token_usage,
                "intent": "request",
                "file_path": file_path,
                "file_content": None,
                "waiting_for_human": False,
            }

        # =========================
        # 1. Lần chạy đầu (chưa có resume_value)
        # =========================
        if not query:
            return {
                "messages": messages,
                "query": "",
                "final_response": "Query rỗng, vui lòng nhập nội dung.",
                "token_usage": token_usage,
                "waiting_for_human": False,
            }

        # Phân loại intent
        intent = await self._classify_intent(query)

        # ===== case 1: question -> trả lời trực tiếp, không HITL =====
        if intent == "question":
            answer = await self._answer_question(query, messages)
            return {
                "messages": messages + [{"role": "assistant", "content": answer}],
                "query": query,
                "final_response": answer,
                "token_usage": token_usage,
                "intent": "question",
                "waiting_for_human": False,
            }

        # ===== case 2: request -> chuẩn bị ghi file, bật human-in-the-loop =====
        file_info = await self._propose_file(query)
        file_path = file_info.file_name
        file_content = file_info.file_content

        # Lưu pending theo thread_id để lần /continue có thông tin
        if thread_id:
            _PENDING_FILE_REQUESTS[thread_id] = {
                "file_path": file_path,
                "file_content": file_content,
                "query": query,
            }

        review_message = (
            f"📝 Tôi đề xuất ghi file sau (CHƯA ghi, cần bạn duyệt):\n\n"
            f"File: {file_path}\n\n"
            f"Nội dung dự kiến:\n{file_content}\n\n"
            f"Hãy trả lời:\n"
            f"- 'đồng ý' để ghi file như trên\n"
            f"- 'từ chối' để hủy bỏ\n"
            f"- Hoặc nhập nội dung file mới nếu bạn muốn chỉnh sửa trước khi ghi."
        )

        return {
            "messages": messages + [{"role": "assistant", "content": review_message}],
            "query": query,
            "final_response": review_message,
            "token_usage": token_usage,
            "intent": "request",
            "file_path": file_path,
            "file_content": file_content,
            "waiting_for_human": True,
            "__interrupt__": True,
        }
