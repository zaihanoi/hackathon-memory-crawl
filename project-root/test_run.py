from pipeline import AIPipeline
from memory import memory_manager

def run_test():
    pipeline = AIPipeline()
    
    # ---------------------------------------------------------
    # KỊCH BẢN 1: CRAWL NHIỀU LOẠI JOB KHÁC NHAU
    # ---------------------------------------------------------
    print("\n--- 1. Luồng Crawl Data (Sync Postgres & Chroma) ---")
    jobs_to_crawl = [
        {
            "job_title": "Senior Python Developer",
            "company_name": "VinAI",
            "salary_range": "3000 - 5000 USD",
            "job_url": "https://vinai.io/jobs/python-01",
            "description": "Phát triển hệ thống xử lý dữ liệu lớn, tối ưu hóa thuật toán RAG.",
            "requirement": "Thành thạo Python, kinh nghiệm với Vector Database (ChromaDB, Pinecone)."
        },
        {
            "job_title": "Kế toán trưởng",
            "company_name": "Bank ABC",
            "salary_range": "20M - 30M VND",
            "job_url": "https://abcbank.com/tuyen-dung/ke-toan",
            "description": "Quản lý dòng tiền, báo cáo thuế và kiểm toán nội bộ.",
            "requirement": "Bằng cử nhân kế toán, chứng chỉ hành nghề, kinh nghiệm 5 năm."
        }
    ]

    for job in jobs_to_crawl:
        jid = pipeline.process_new_job(job)
        print(f"-> Đã lưu Job: {job['job_title']} (ID: {jid})")

    # ---------------------------------------------------------
    # KỊCH BẢN 2: ĐĂNG KÝ USER VỚI SKILLS CỤ THỂ
    # ---------------------------------------------------------
    print("\n--- 2. Luồng User Profile (Kỹ sư IT) ---")
    user_name = "Nguyễn Triết"
    user_email = "triet.ai@example.com"
    user_exps = [
        {"category": "skill", "text": "Chuyên gia lập trình Python và xử lý dữ liệu với SQL."},
        {"category": "project", "text": "Xây dựng AI Agent hỗ trợ tìm việc sử dụng RAG và ChromaDB."},
        {"category": "education", "text": "Tốt nghiệp ngành Công nghệ thông tin loại Giỏi."}
    ]
    
    u_id = pipeline.register_user(user_name, user_email, user_exps)

    # ---------------------------------------------------------
    # KỊCH BẢN 3: KIỂM TRA ĐỘ KHỚP (MATCHING)
    # ---------------------------------------------------------
    print("\n--- 3. Kiểm tra Phân tích độ khớp (Semantic Match) ---")
    
    # Giả sử Agent lấy "Skills" của User để đi so sánh với kho Job
    query_cv = "Tôi là kỹ sư phần mềm chuyên về Python và các hệ thống AI sử dụng Vector DB."
    
    # Tìm top 2 job liên quan nhất
    results = memory_manager.analyze_job_match(query_cv, n_results=2)
    
    for match in results:
        score = match['match_score']
        status = "✅ PHÙ HỢP" if score >= 0.75 else "❌ KHÔNG KHỚP"
        
        print(f"[{status}]")
        print(f"- Job: {match['company']} ({match['job_id']})")
        print(f"- Độ khớp: {score}")
        print("-" * 30)

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Lỗi thực thi: {e}")
