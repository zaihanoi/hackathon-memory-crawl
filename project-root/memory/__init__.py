from .chroma_manager import ChromaManager

# Khởi tạo một instance duy nhất (Singleton) để dùng chung toàn dự án
# Tránh việc nhiều file cùng mở kết nối tới DB gây khóa file (Database lock)
memory_manager = ChromaManager()

__all__ = ["memory_manager", "ChromaManager"]
