import chromadb
from chromadb.utils import embedding_functions
from .config import CHROMA_DATA_PATH, COLLECTIONS

class ChromaManager:
    def __init__(self):
        # 1. Khởi tạo Persistent Client (Lưu trữ vật lý)
        self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        
        # 2. Embedding Function (Mặc định: all-MiniLM-L6-v2)
        # Model này nhẹ, chạy tốt trên máy cá nhân khi thi Hackathon
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()

        # 3. Khởi tạo các Collections theo sơ đồ AI Agent
        self.job_col = self.client.get_or_create_collection(
            name=COLLECTIONS["JOBS"], embedding_function=self.embed_fn
        )
        self.user_col = self.client.get_or_create_collection(
            name=COLLECTIONS["USER_PROFILE"], embedding_function=self.embed_fn
        )
        self.mail_col = self.client.get_or_create_collection(
            name=COLLECTIONS["EMAILS"], embedding_function=self.embed_fn
        )
        self.pref_col = self.client.get_or_create_collection(
            name=COLLECTIONS["PREFERENCES"], embedding_function=self.embed_fn
        )

    # --- CHỨC NĂNG 1: LƯU JOB CRAWL (Khối CRAWL DATA) ---
    def save_job_vector(self, job_id, title, company, salary, link, description, requirement):
        """
        Gộp tất cả thông tin vào Document để AI có cái nhìn tổng thể về Job.
        Lưu các thông tin tra cứu nhanh vào Metadata.
        """
        # Cấu trúc nội dung để Embedding (AI sẽ "đọc" đoạn này)
        combined_content = (
            f"Công ty: {company}\n"
            f"Vị trí: {title}\n"
            f"Mức lương: {salary}\n"
            f"Link chi tiết: {link}\n"
            f"Mô tả công việc: {description}\n"
            f"Yêu cầu ứng viên: {requirement}"
        )

        self.job_col.upsert(
            ids=[str(job_id)],
            documents=[combined_content],
            metadatas=[{
                "job_id": job_id,
                "company": company,
                "salary": salary, # Lưu để lọc (filtering) nếu cần
                "link": link
            }]
        )
    def analyze_job_match(self, user_cv_text, n_results=10):
        """
        So sánh CV và JD. Trả về điểm số trong khoảng [0, 1].
        """
        results = self.job_col.query(
            query_texts=[user_cv_text],
            n_results=n_results,
            include=["metadatas", "distances"]
        )

        matches = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                # Distance trong ChromaDB (thường là L2) càng nhỏ thì càng giống
                distance = results['distances'][0][i]
                
                # Chuyển đổi sang Match Score (0.0 - 1.0)
                # Công thức: score = 1 - distance (giới hạn trong khoảng 0-1)
                match_score = max(0.0, min(1.0, 1.0 - distance))
                
                matches.append({
                    "job_id": results['metadatas'][0][i]['job_id'],
                    "company": results['metadatas'][0][i]['company'],
                    "salary": results['metadatas'][0][i].get('salary'),
                    "match_score": round(float(match_score), 4) # Lấy 4 chữ số thập phân
                })
        
        return sorted(matches, key=lambda x: x['match_score'], reverse=True)

    # --- CHỨC NĂNG 2: LƯU KINH NGHIỆM USER (Khối AI AGENT VIẾT CV) ---
    def save_user_experience(self, user_id, exp_text, category="project"):
        """Lưu các 'mảnh' kinh nghiệm của User để RAG khi viết CV"""
        uid = f"u_{user_id}_{hash(exp_text)}"
        self.user_col.add(
            ids=[uid],
            documents=[exp_text],
            metadatas={"user_id": user_id, "category": category}
        )

    # --- CHỨC NĂNG 3: LƯU MAIL (Khối ĐỌC MAIL) ---
    def save_mail_context(self, app_id, mail_body, sentiment):
        """Lưu ngữ cảnh mail để Agent tư vấn phản hồi"""
        mid = f"mail_{app_id}_{hash(mail_body[:30])}"
        self.mail_col.add(
            ids=[mid],
            documents=[mail_body],
            metadatas={"app_id": app_id, "sentiment": sentiment}
        )

    # --- CHỨC NĂNG SEARCH CHÍNH ---
    def search_jobs_by_query(self, query_text, n_results=5):
        """Dùng cho khối 'Phân tích độ khớp'"""
        return self.job_col.query(
            query_texts=[query_text],
            n_results=n_results
        )
    
