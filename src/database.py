import sqlite3

DB_FILE = "jobs.db"


def init_db():
    """Khởi tạo database với schema dành cho Ứng viên (Khớp với AI mới)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_nhom TEXT,
            raw_content TEXT,
            full_content TEXT,
            nguoi_gui TEXT,
            url_bai_viet TEXT,
            url_nhom TEXT,
            label TEXT,
            visa_mong_muon TEXT,
            nganh_nghe TEXT,
            trinh_do_tieng_nhat TEXT,
            gioi_tinh TEXT,
            dia_diem TEXT,
            luong_mong_muon TEXT,
            yeu_cau_khac TEXT,
            dai_ngo TEXT,
            so_dien_thoai TEXT,
            zalo TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Đã tạo database (bảng candidates)!")


def save_job(post):
    """
    Lưu 1 ứng viên vào SQLite.
    Trả về True nếu lưu thành công, False nếu lỗi.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    analyzed = post.get('analyzed', {})

    try:
        c.execute('''
            INSERT INTO candidates (
                ten_nhom, raw_content, full_content, nguoi_gui,
                url_bai_viet, url_nhom, label, visa_mong_muon, nganh_nghe,
                trinh_do_tieng_nhat, gioi_tinh, dia_diem, luong_mong_muon,
                yeu_cau_khac, dai_ngo, so_dien_thoai, zalo, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.get('ten_nhom', ''),
            post.get('raw_content', ''),
            post.get('full_content', ''),
            post.get('nguoi_gui', ''),
            post.get('url_bai_viet', ''),
            post.get('url_nhom', ''),
            post.get('label', ''),
            analyzed.get('visa_mong_muon', ''),
            analyzed.get('nganh_nghe', ''),
            analyzed.get('trinh_do_tieng_nhat', ''),
            analyzed.get('gioi_tinh', ''),
            analyzed.get('dia_diem', ''),
            analyzed.get('luong_mong_muon', ''),
            analyzed.get('yeu_cau_khac', ''),
            analyzed.get('dai_ngo', ''),
            analyzed.get('so_dien_thoai', ''),
            analyzed.get('zalo', ''),
            analyzed.get('summary', '')
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def is_post_exists(content: str) -> bool:
    """Kiểm tra bài viết đã tồn tại trong database chưa"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM candidates WHERE full_content = ?", (content,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0


def search_jobs(keyword=None, location=None):
    """Tìm kiếm ứng viên trong database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = "SELECT * FROM candidates WHERE 1=1"
    params = []

    if keyword:
        query += " AND raw_content LIKE ?"
        params.append(f"%{keyword}%")
    if location:
        query += " AND dia_diem LIKE ?"
        params.append(f"%{location}%")

    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results


def view_all_jobs():
    """Xem tất cả ứng viên trong database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, ten_nhom, gioi_tinh, trinh_do_tieng_nhat, so_dien_thoai, summary FROM candidates")
    rows = c.fetchall()
    conn.close()

    print(f"\n📊 Tổng số ứng viên: {len(rows)}\n")
    for row in rows:
        print(f"ID: {row[0]} | Nhóm: {row[1][:30]}...")
        print(f"   Giới tính: {row[2]} | Tiếng Nhật: {row[3]} | SĐT: {row[4]}")
        print(f"   Tóm tắt: {row[5][:80]}...")
        print("-" * 60)