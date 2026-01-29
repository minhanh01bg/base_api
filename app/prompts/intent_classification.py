"""
Intent Classification Prompt - Prompt để phân loại intent từ user query.
"""

INTENT_CLASSIFICATION_PROMPT = """Phân loại intent của câu sau đây. Chỉ trả về một trong hai từ: "question" hoặc "request".

- "question": Nếu đây là câu hỏi bình thường, yêu cầu thông tin, giải thích, hoặc trò chuyện.
- "request": Nếu đây là yêu cầu thực hiện hành động như ghi file, tạo file, lưu dữ liệu, hoặc bất kỳ hành động nào cần được phê duyệt.

Câu cần phân loại: "{query}"

Chỉ trả về một từ: question hoặc request"""

