from postgreDB.db_manager import PostgresManager
from memory import memory_manager

class AIPipeline:
    def __init__(self):
        self.db = PostgresManager()
        self.vector_db = memory_manager

    def process_new_job(self, job_data):
        """
        Đầu vào job_data cần các key: 
        company_name, job_title, salary_range, job_url, description, requirement
        """
        # 1. Lưu vào PostgreSQL để lấy job_id
        job_id = self.db.insert_job(job_data)
        
        # 2. Đồng bộ sang ChromaDB để phục vụ tìm kiếm ngữ nghĩa và tính Match Score
        # Chúng ta truyền thêm description và requirement vào ChromaDB
        self.vector_db.save_job_vector(
            job_id=job_id,
            title=job_data['job_title'],
            company=job_data['company_name'],
            salary=job_data['salary_range'],
            link=job_data['job_url'],
            description=job_data['description'],
            requirement=job_data['requirement']
        )
        
        # 3. Đánh dấu đã xử lý (nếu cần)
        self.db.update_job_processed_status(job_id, True)
        
        return job_id
    def register_user(self, name, email, experiences):
        """
        Lưu User vào Postgres và các mảnh kinh nghiệm vào ChromaDB.
        Đảm bảo tính nhất quán dữ liệu giữa SQL và Vector DB.
        """
        # 1. Gọi hàm insert_user đã có trong db_manager để lấy ID thực từ Postgres
        user_id = self.db.insert_user(name, email)
        
        # 2. Duyệt qua danh sách kinh nghiệm để lưu vào ChromaDB
        for exp in experiences:
            self.vector_db.save_user_experience(
                user_id=user_id,
                exp_text=exp['text'],
                category=exp['category']
            )
        
        print(f"--- Đã đăng ký thành công User: {name} (ID: {user_id}) ---")
        return user_id
    
