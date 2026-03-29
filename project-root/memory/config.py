import os

# Đường dẫn tuyệt đối đến thư mục lưu trữ để tránh lỗi "không tìm thấy folder"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DATA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")

# Đảm bảo thư mục tồn tại
if not os.path.exists(CHROMA_DATA_PATH):
    os.makedirs(CHROMA_DATA_PATH)

# Cấu hình các Collection tương ứng sơ đồ
COLLECTIONS = {
    "JOBS": "job_details",
    "USER_PROFILE": "user_experience",
    "EMAILS": "mail_history",
    "PREFERENCES": "user_feedback"
}
