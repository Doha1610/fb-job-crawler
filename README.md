

# 🇯🇵 Japan Job Finder - AI-Powered Recruitment Crawler

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Scraping-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)

Dự án tự động thu thập, phân tích và cấu trúc hóa dữ liệu tuyển dụng đi Nhật Bản từ các hội nhóm Facebook. Hệ thống sử dụng AI (OpenAI GPT) và OCR (Tesseract) để trích xuất thông tin từ văn bản và hình ảnh, giúp tiết kiệm 90% thời gian lọc tin thủ công.

## 🌟 Tính năng nổi bật (Features)

- **🕷️ Multi-Group Crawler:** Tự động thu thập bài viết từ nhiều nhóm Facebook cùng lúc.
- **🔐 Cookie Management:** Tự động lưu và tái sử dụng session đăng nhập (không cần login lại mỗi lần chạy).
- **🧠 AI-Powered Extraction (2-Stage Pipeline):** 
  - *Tầng 1:* Tách một bài viết chứa nhiều đơn hàng thành các job riêng biệt.
  - *Tầng 2:* Trích xuất dữ liệu có cấu trúc (Visa, Ngành nghề, Lương, Địa điểm, Trình độ tiếng Nhật...).
- **👁️ OCR Fallback:** Tự động dùng Tesseract OCR để đọc chữ từ ảnh nếu bài viết không có văn bản.
- **🧹 Smart Classification:** Lọc bỏ tin rác (Spam) và bài của ứng viên, chỉ giữ lại tin tuyển dụng thực sự.
- **📊 Dual Storage:** Lưu trữ dữ liệu sạch vào SQLite và đồng bộ lên Google Sheets.
- **⏱️ Time-based Filtering:** Chỉ lấy các bài đăng trong vòng 3 giờ gần nhất.

## 🏗️ Kiến trúc hệ thống (Architecture)

```text
[Facebook Groups] 
       │
       ▼
[Selenium Crawler] ──(Login via Cookies)
       │
       ├──▶ (Nếu có Text) ──▶ [AI Analyzer (GPT)]
       │
       └──▶ (Nếu chỉ có Ảnh) ──▶ [OCR (Tesseract)] ──▶ [AI Analyzer (GPT)]
                                      │
                                      ▼
                            [Rules Engine (Normalization)]
                                      │
                                      ▼
                        [SQLite DB] & [Google Sheets API]
```

## 🚀 Hướng dẫn cài đặt (Installation)

### 1. Yêu cầu hệ thống
- Python 3.10+
- Google Chrome (phiên bản mới nhất)
- Tesseract OCR (đã cài đặt và thêm vào biến môi trường PATH)

### 2. Cài đặt các thư viện
```bash
# Clone dự án
git clone https://github.com/Doha1610/Video-transcription-ai.git
cd facebook-job-finder-crm

# Tạo môi trường ảo
python -m venv .venv
.venv\Scripts\activate  # Trên Windows
# source .venv/bin/activate  # Trên Mac/Linux

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Tạo file `.env` ở thư mục gốc và thêm các key sau:
```env
OPENAI_API_KEY=your_openai_api_key_here
# Nếu dùng API proxy (như xah.io, ckey...):
OPENAI_BASE_URL=https://api.xah.io/v1
```

### 4. Cấu hình Google Sheets (Tùy chọn)
1. Tạo Service Account trên Google Cloud Console.
2. Bật Google Sheets API.
3. Tải file JSON credentials, đổi tên thành `google_credentials.json` và để ở thư mục gốc.
4. Share Google Sheet của bạn cho email Service Account (quyền Editor).
5. Cập nhật `SPREADSHEET_ID` trong file `src/google_sheets.py`.

## 💻 Cách sử dụng (Usage)

### Cấu hình danh sách nhóm
Thêm các link group Facebook cần crawl vào file `groups.txt` (mỗi dòng 1 link):
```text
https://www.facebook.com/groups/tokuteiginothucpham.japan
https://www.facebook.com/groups/nhatban.tuyendung
```

### Chạy Crawler
```bash
python main.py
```

*Lần đầu chạy, trình duyệt sẽ mở ra và yêu cầu bạn đăng nhập Facebook. Sau khi đăng nhập xong, nhấn Enter trên Terminal, hệ thống sẽ tự động lưu cookies cho các lần chạy sau.*

## 📂 Cấu trúc thư mục (Project Structure)

```text
├── src/
│   ├── crawl.py            # Core crawler logic
│   ├── multi_crawler.py    # Quản lý crawl nhiều group
│   ├── ai_analyzer.py      # AI pipeline (Split & Extract)
│   ├── ocr.py              # Xử lý ảnh với Tesseract
│   ├── classifier.py       # Lọc tin rác / ứng viên
│   ├── rules_engine.py     # Chuẩn hóa dữ liệu bằng rules
│   ├── database.py         # Tương tác SQLite
│   ├── google_sheets.py    # Đồng bộ Google Sheets
│   └── cookie_manager.py   # Quản lý session Facebook
├── groups.txt              # Danh sách URL group
├── main.py                 # Entry point
└── requirements.txt        # Dependencies
```

## 🛠️ Công nghệ sử dụng (Tech Stack)
- **Ngôn ngữ:** Python
- **Crawler:** Selenium WebDriver
- **AI/NLP:** OpenAI API (GPT-3.5/GPT-4)
- **Computer Vision:** Tesseract OCR, Pillow
- **Database:** SQLite3
- **Cloud Integration:** Google Sheets API

## 🗺️ Lộ trình phát triển (Roadmap)
- [x] Crawler cơ bản với Selenium.
- [x] Tích hợp AI trích xuất dữ liệu.
- [x] Xử lý ảnh bằng OCR.
- [x] Lưu trữ SQLite & Google Sheets.
- [ ] Xây dựng Dashboard quản lý bằng Streamlit.
- [ ] Tích hợp AI Matching (Gợi ý việc làm cho ứng viên).
- [ ] Xây dựng REST API (FastAPI).



