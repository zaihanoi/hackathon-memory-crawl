import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
from datetime import datetime
import re



# API
url = "https://ms.vietnamworks.com/job-search/v1.0/search"

headers = {
    "Accept": "*/*",
    "Accept-Language": "vi",
    "Content-Type": "application/json",
    "Origin": "https://www.vietnamworks.com",
    "Referer": "https://www.vietnamworks.com/",
    "User-Agent": "Mozilla/5.0",
    "X-Source": "Page-Container"
}

payload = {
    "userId": 0,
    "query": "",
    "filter": [],
    "ranges": [],
    "order": [],
    "hitsPerPage": 50,
    "page": 0,
    "retrieveFields": [
        "jobId", "alias", "jobTitle", "companyName", "isSalaryVisible", 
        "salaryMin", "salaryMax", "jobDescription", "jobRequirement",
        "expiredOn"
    ],
    "summaryVersion": ""
}



# Deep crawl job detail
def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

# Cái này chuyển đổi các mã unicode escape (ví dụ: \u003c thành <, \u003e thành >)
def unescape_unicode(text):
    if not text: return ""
    return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)

def get_job_detail(session, job_link):
    if not job_link: return {"des": "", "req": "", "address": ""}

    try:
        res = session.get(job_link, timeout=10)
        res.raise_for_status()
        
        # Lấy tất cả các đoạn chuỗi payload của Next.js App Router
        chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', res.text)
        
        payload = ""
        for chunk in chunks:
            try:
                payload += json.loads('"' + chunk + '"')
            except:
                continue
                
        # Xử lý Description và Requ
        desc_match = re.search(r'"jobDescription":"(.*?)"', payload)
        req_match = re.search(r'"jobRequirement":"(.*?)"', payload)
        
        def extract_content(match_val):
            if not match_val: return ""
            if match_val.startswith('$'):
                ref_id = match_val[1:]
                content_match = re.search(rf'\b{ref_id}:T([0-9a-f]+),(.*)', payload, re.DOTALL)
                if content_match:
                    hex_length = content_match.group(1)
                    text_content = content_match.group(2)
                    try:
                        exact_byte_len = int(hex_length, 16)
                        text_bytes = text_content.encode('utf-8')
                        extracted_bytes = text_bytes[:exact_byte_len]
                        return extracted_bytes.decode('utf-8', errors='ignore')
                    except Exception:
                        pass
            return match_val
            
        desc_html = extract_content(desc_match.group(1)) if desc_match else ""
        req_html = extract_content(req_match.group(1)) if req_match else ""
        
        desc_html = unescape_unicode(desc_html)
        req_html = unescape_unicode(req_html)

        # Lấy địa chỉ chi tiết
        # Tìm tất cả các chuỗi có dạng "address"
        address_matches = re.findall(r'"address":"(.*?)"', payload)
        
        # Lọc bỏ các địa chỉ rỗng và loại bỏ trùng lặp
        unique_addresses = list(dict.fromkeys([addr for addr in address_matches if addr]))
        
        # Nối các địa chỉ lại bằng dấu trong trường hợp công ty có nhiều chi nhánh
        detailed_address = " | ".join(unique_addresses)
        
        # Giải mã unicode cho địa chỉ (nếu có tiếng Việt)
        detailed_address = unescape_unicode(detailed_address)

        return {
            "des": clean_html(desc_html),
            "req": clean_html(req_html),
            "address": detailed_address
        }

    except Exception as e:
        print(f"Lỗi khi cào trang chi tiết {job_link}: {e}")
        return {"des": "", "req": "", "address": ""}
    


# Format
def format_salary(job):
    if not job.get("isSalaryVisible"):
        return "Thương lượng"
   
    min_sal = job.get("salaryMin")
    max_sal = job.get("salaryMax")
   
    if min_sal and max_sal:
        return f"{min_sal} - {max_sal}"
    elif min_sal:
        return f"Từ {min_sal}"
    elif max_sal:
        return f"Lên đến {max_sal}"
    
    return "Thương lượng"

def format_expiration_date(expired_on_str):
    if not expired_on_str:
        return ""
    try:
        expire_date = datetime.fromisoformat(expired_on_str)
        return expire_date.strftime("%d/%m")
    except Exception:
        return expired_on_str



# Main loop
all_jobs = []
seen_ids = set()

# Target
TARGET_JOBS = 3
page = 0

# Timer
start_time = time.time()

with requests.Session() as session:
    session.headers.update(headers)
    session.get("https://www.vietnamworks.com")

    while len(all_jobs) < TARGET_JOBS:
        payload["page"] = page
        print(f"Crawling page {page}...")

        # Timeout
        try:
            res = session.post(url, json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            print(f"Error at page {page}: {e}")
            page += 1
            time.sleep(2)
            continue

        jobs = data.get("data", [])
        
        if not jobs:
            print("Out of data")
            break  

        for job in jobs:
            job_id = job.get("jobId")
            if job_id is None or job_id in seen_ids:
                continue
        
            seen_ids.add(job_id)
            alias = job.get("alias", "")
            job_link =  f"https://www.vietnamworks.com/{alias}-{job_id}-jv" if alias else None

            detail_info = get_job_detail(session, job_link)

            all_jobs.append({
                "title": job.get("jobTitle"),
                "company": job.get("companyName"),
                "salary": format_salary(job),
                "link": job_link,
                "expires_date": "Hết hạn vào " + format_expiration_date(job.get("expiredOn")),
                "description": detail_info.get("des", ""),
                "requirement": detail_info.get("req", ""),
                "address": detail_info.get("address", "")
            })

            if len(all_jobs) == TARGET_JOBS:
                print("Finished")
                break

        page += 1
        time.sleep(1)



df = pd.DataFrame(all_jobs)

print(df.head())
print("Jobs: ", len(df))

# df.to_csv("jobs_vietnamworks.csv", index=False, encoding="utf-8-sig")



# End timer
end_time = time.time()
elapsed_time = end_time - start_time

minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Total time: {minutes} minutes {seconds} seconds ({elapsed_time:.2f}s)")



# SỬA LẠI ĐOẠN NÀY ĐỂ NỐI NHÉ TRIET
from sqlalchemy import create_engine

df = pd.DataFrame(all_jobs)

# Cấu hình chuỗi kết nối PostgreSQL: postgresql://[user]:[password]@[host]:[port]/[database_name]
engine = create_engine('postgresql://postgres:123456@localhost:5432/vietnamworks_db')

# Đẩy data vào bảng 'jobs', nếu bảng đã tồn tại thì thêm dữ liệu vào cuối (append)
df.to_sql('jobs', engine, if_exists='append', index=False)
print("Đã lưu vào PostgreSQL thành công!")

