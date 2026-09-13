import sqlite3
import json

DB_FILE = "jobs.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_content TEXT,
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    analyzed = post['analyzed']
    c.execute('''
        INSERT INTO jobs (
            raw_content, visa_type, industry, japanese_level,
            gender, location, salary, requirements, benefits, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        post['raw_content'],
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
    conn.close()
    print("✅ Đã lưu vào database!")


def search_jobs(keyword=None, visa=None, location=None):
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