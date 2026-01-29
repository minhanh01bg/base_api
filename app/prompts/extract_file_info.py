"""
Extract File Info Prompt - Prompt để LLM tự viết file_name và file_content dựa trên user query.
"""

EXTRACT_FILE_INFO_PROMPT = """Dựa trên yêu cầu của người dùng, hãy tạo thông tin file:
- file_name: Tên file (ví dụ: "output.txt", "data.json", "notes.md"). Chỉ trả về tên file, KHÔNG bao gồm đường dẫn.
- file_content: Nội dung file cần ghi (LLM tự viết dựa trên yêu cầu)

Câu yêu cầu: "{query}"

Lưu ý:
- Tên file: Nếu người dùng KHÔNG chỉ định tên file cụ thể, hãy TỰ ĐỀ XUẤT một tên file hợp lý dựa trên nội dung yêu cầu (ví dụ: "output.txt", "document.md", "data.json")
- Tên file: Nếu người dùng CÓ chỉ định tên file, hãy sử dụng tên đó
- Nội dung file: LLM phải TỰ VIẾT nội dung file dựa trên yêu cầu của người dùng, KHÔNG chỉ trích xuất từ query
- Chỉ trả về tên file, không bao gồm đường dẫn thư mục"""

