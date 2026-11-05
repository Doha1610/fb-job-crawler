
import sqlite3

DB_FILE = "jobs.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        c.execute("""
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
        """)

        conn.commit()
        print("✅ Đã khởi tạo database candidates!")

    finally:
        conn.close()


def is_post_exists(content: str, url: str = "") -> bool:
    """Kiểm tra bài đăng đã tồn tại theo URL hoặc nội dung."""

    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        if url:
            c.execute(
                "SELECT 1 FROM candidates WHERE url_bai_viet = ? LIMIT 1",
                (url,)
            )

            if c.fetchone():
                return True

        c.execute(
            "SELECT 1 FROM candidates WHERE full_content = ? LIMIT 1",
            (content,)
        )

        return c.fetchone() is not None

    finally:
        conn.close()


def save_job(post: dict) -> bool:
    """
    Chỉ lưu dữ liệu đã được xác định là ứng viên.
    Trả về True nếu lưu thành công.
    """

    if post.get("label") != "ỨNG VIÊN":
        print("⚠️ Không lưu: bản ghi không phải ứng viên.")
        return False

    analyzed = post.get("analyzed", {})

    if not analyzed:
        print("⚠️ Không lưu: chưa có dữ liệu AI.")
        return False

    content = post.get("full_content", "")
    url = post.get("url_bai_viet", "")

    if is_post_exists(content, url):
        print("⚠️ Bài đăng đã tồn tại, không lưu trùng.")
        return False

    special_conditions = analyzed.get("specialConditions", [])

    if isinstance(special_conditions, list):
        special_conditions = "; ".join(special_conditions)

    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        c.execute("""
            INSERT INTO candidates (
                ten_nhom,
                raw_content,
                full_content,
                nguoi_gui,
                url_bai_viet,
                url_nhom,
                label,
                visa_mong_muon,
                nganh_nghe,
                trinh_do_tieng_nhat,
                gioi_tinh,
                dia_diem,
                luong_mong_muon,
                yeu_cau_khac,
                dai_ngo,
                so_dien_thoai,
                zalo,
                summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post.get("ten_nhom", ""),
            post.get("raw_content", ""),
            content,
            post.get("nguoi_gui", ""),
            url,
            post.get("url_nhom", ""),
            "ỨNG VIÊN",
            analyzed.get("visa", ""),
            analyzed.get("job", ""),
            analyzed.get("languageLevel", ""),
            analyzed.get("gender", ""),
            analyzed.get("workLocation", ""),
            "",
            special_conditions,
            "",
            "",
            "",
            analyzed.get("makeAI", "")
        ))

        conn.commit()
        print("💾 Đã lưu ứng viên vào SQLite.")
        return True

    except sqlite3.Error as e:
        print(f"❌ Lỗi lưu SQLite: {e}")
        return False

    finally:
        conn.close()


def search_jobs(keyword=None, location=None):
    conn = sqlite3.connect(DB_FILE)

    try:
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
        return c.fetchall()

    finally:
        conn.close()


def view_all_jobs():
    conn = sqlite3.connect(DB_FILE)

    try:
        c = conn.cursor()

        c.execute("""
            SELECT
                id,
                ten_nhom,
                nguoi_gui,
                visa_mong_muon,
                nganh_nghe,
                trinh_do_tieng_nhat,
                gioi_tinh,
                dia_diem,
                summary
            FROM candidates
            ORDER BY id DESC
        """)

        rows = c.fetchall()

        print(f"\n📊 Tổng số ứng viên: {len(rows)}\n")

        for row in rows:
            print(f"ID: {row[0]}")
            print(f"Nhóm: {row[1]}")
            print(f"Người đăng: {row[2]}")
            print(f"Visa: {row[3]}")
            print(f"Ngành nghề: {row[4]}")
            print(f"Tiếng Nhật: {row[5]}")
            print(f"Giới tính: {row[6]}")
            print(f"Khu vực: {row[7]}")
            print(f"Tóm tắt: {row[8]}")
            print("-" * 60)

        return rows

    finally:
        conn.close()
