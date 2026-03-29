-- Bảng 1: Thông tin người dùng (Khối Thông tin user)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    professional_summary TEXT, -- Tóm tắt ngắn để AI định hướng
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 2: Dữ liệu việc làm (Khối CRAWL DATA)
CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    job_title VARCHAR(255),
    salary_range VARCHAR(100),
    
    job_url TEXT UNIQUE, 
    
    is_processed BOOLEAN DEFAULT FALSE, -- Đã được AI phân tích chưa?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
drop table jobs
-- Bảng 3: Kho lưu trữ CV (Khối BACKEND & AI AGENT Viết CV)
CREATE TABLE IF NOT EXISTS user_cvs (
    cv_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    cv_name VARCHAR(255), -- VD: "CV Java Backend - FPT"
    file_path TEXT, 
    is_customized BOOLEAN DEFAULT FALSE, -- CV gốc hay CV đã tối ưu cho JD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 4: Quản lý ứng tuyển (Khối OUTPUT & Muốn apply)
CREATE TABLE IF NOT EXISTS applications (
    app_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    job_id INT REFERENCES jobs(job_id),
    cv_id INT REFERENCES user_cvs(cv_id),
    match_score FLOAT, -- Điểm phần trăm khớp (85%, 60%...)
    status VARCHAR(50) DEFAULT 'Pending', -- Pending, Applied, Interviewing, Rejected
    applied_at TIMESTAMP,
    UNIQUE(user_id, job_id)
);

-- Bảng 5: Lịch sử Email (Khối CrewAI Đọc mail)
CREATE TABLE IF NOT EXISTS interaction_logs (
    log_id SERIAL PRIMARY KEY,
    app_id INT REFERENCES applications(app_id),
    direction VARCHAR(10) CHECK (direction IN ('IN', 'OUT')), -- IN: Nhà tuyển dụng gửi, OUT: Agent gửi
    subject TEXT,
    sentiment VARCHAR(20), -- Positive, Negative, Neutral
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from jobs