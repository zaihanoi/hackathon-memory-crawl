import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresManager:
    def __init__(self):
        # Thông số kết nối (Hãy thay đổi theo DB của team bạn)
        self.conn = psycopg2.connect(
            dbname="hackathon_demo1",
            user="postgres",
            password="@Ductriet66",
            host="localhost",
            port="5432"
        )
        self.conn.autocommit = True

    def insert_job(self, job_data):
        """Khớp chính xác với Schema: company_name, job_title, salary_range, job_url"""
        query = """
        INSERT INTO jobs (company_name, job_title, salary_range, job_url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (job_url) 
        DO UPDATE SET company_name = EXCLUDED.company_name -- Cập nhật giả để lấy ID
        RETURNING job_id;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (
                job_data['company_name'], 
                job_data['job_title'], 
                job_data['salary_range'], 
                job_data['job_url']
            ))
            return cur.fetchone()[0]
    def insert_user(self, name, email):
        """Khớp với Schema: full_name, email"""
        query = """
        INSERT INTO users (full_name, email) 
        VALUES (%s, %s) 
        ON CONFLICT (email) 
        DO UPDATE SET full_name = EXCLUDED.full_name
        RETURNING user_id;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (name, email))
            return cur.fetchone()[0]

    def update_job_processed_status(self, job_id, status=True):
        """Cập nhật cột is_processed sau khi AI phân tích xong"""
        query = "UPDATE jobs SET is_processed = %s WHERE job_id = %s"
        with self.conn.cursor() as cur:
            cur.execute(query, (status, job_id))
