import sqlite3

DB_FILE = "jobs.db"


def init_db():
    """Khởi tạo database với schema đầy đủ"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_nhom TEXT,
            raw_content TEXT,
            nguoi_gui TEXT,
            url_bai_viet TEXT,
            url_nhom TEXT,
            label TEXT,
            visa_type TEXT,
            industry TEXT,
            japanese_level TEXT,
            gender TEXT,
            location TEXT,
            salary TEXT,
            requirements TEXT,
            benefits TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Đã tạo database!")


def save_job(post):
    """
    Lưu 1 bài vào SQLite.
    Trả về True nếu lưu thành công, False nếu lỗi.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    analyzed = post.get('analyzed', {})

    try:
        c.execute('''
            INSERT INTO jobs (
                ten_nhom, raw_content, nguoi_gui, url_bai_viet, url_nhom,
                label, visa_type, industry, japanese_level,
                gender, location, salary, requirements, benefits, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.get('ten_nhom', ''),
            post.get('raw_content', ''),
            post.get('nguoi_gui', ''),
            post.get('url_bai_viet', ''),
            post.get('url_nhom', ''),
            post.get('label', ''),
            analyzed.get('visa_type', ''),
            analyzed.get('industry', ''),
            analyzed.get('japanese_level', ''),
            analyzed.get('gender', ''),
            analyzed.get('location', ''),
            analyzed.get('salary', ''),
            analyzed.get('requirements', ''),
            analyzed.get('benefits', ''),
            analyzed.get('summary', '')
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def search_jobs(keyword=None, visa=None, location=None):
    """Tìm kiếm job trong database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if keyword:
        query += " AND raw_content LIKE ?"
        params.append(f"%{keyword}%")
    if visa:
        query += " AND visa_type LIKE ?"
        params.append(f"%{visa}%")
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results


def view_all_jobs():
    """Xem tất cả job trong database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, ten_nhom, label, visa_type, summary FROM jobs")
    rows = c.fetchall()
    conn.close()

    print(f"\n📊 Tổng số bài: {len(rows)}\n")
    for row in rows:
        print(f"ID: {row[0]} | Nhóm: {row[1][:30]}... | Nhãn: {row[2]}")
        print(f"   Visa: {row[3]} | Tóm tắt: {row[4][:80]}...")
        print("-" * 60)