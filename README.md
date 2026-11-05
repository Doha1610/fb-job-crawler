# 🇯🇵 Japan Candidate Sourcing - AI-Powered CRM Crawler

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Scraping-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)

Dự án tự động thu thập, phân loại và trích xuất **hồ sơ ứng viên đi Nhật** từ các hội nhóm Facebook. Hệ thống sử dụng AI (OpenAI GPT) để bóc tách thông tin từ văn bản, lọc bỏ nhiễu (bài của nhà tuyển dụng, comment rác) và lưu trữ dữ liệu có cấu trúc vào Database/CRM, giúp các đơn vị môi giới tiết kiệm 90% thời gian tìm kiếm và liên hệ ứng viên tiềm năng.

## 🌟 Tính năng nổi bật (Features)

- **🎯 Candidate-Focused Crawler:** Chỉ thu thập bài đăng của **người lao động đang tìm việc**, loại bỏ hoàn toàn bài đăng của đối thủ (cò môi giới, công ty tuyển dụng).
- **🔐 Cookie Management:** Tự động lưu và tái sử dụng session đăng nhập qua Chrome Profile (không cần login lại mỗi lần chạy).
- **🧹 Smart Classification:** Sử dụng bộ lọc từ khóa chặt chẽ để phân biệt chính xác giữa "Ứng viên", "Nhà tuyển dụng" và "Comment/Spam".
- **🧠 AI-Powered Extraction (Structured Outputs):** 
  - Trích xuất chính xác thông tin ứng viên: Visa mong muốn, Ngành nghề, Địa điểm, Trình độ tiếng Nhật, Giới tính, Nguyện vọng...
  - Sử dụng **JSON Schema** để ép AI trả về đúng cấu trúc, chống ảo giác (hallucination).
- **👁️ OCR Fallback:** Tự động dùng Tesseract OCR để đọc chữ từ ảnh nếu bài viết không có văn bản.
- **📊 Dual Storage:** Lưu trữ dữ liệu sạch vào **SQLite** và đồng bộ lên **Google Sheets**.
- **⏱️ Time-based Filtering:** Hỗ trợ quét bài viết theo khung thời gian (3 giờ gần nhất hoặc 3 ngày gần nhất).

## 🏗️ Kiến trúc hệ thống (Architecture)

```text
[Facebook Groups] 
       │
       ▼
[Selenium Crawler] ──(Load Chrome Profile)
       │
       ├──▶ (Lấy nội dung bài đăng gốc) ──▶ [Classifier (Lọc Ứng viên)]
       │                                              │
       │                                              ▼
       └──▶ (Nếu không có Text) ──▶ [OCR] ──▶ [AI Analyzer (JSON Schema)]
                                                      │
                                                      ▼
                                            [Rules Engine (Normalize)]
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

Dự án cung cấp 2 chế độ chạy độc lập:

### 1. Chạy chế độ quét nhanh (3 giờ gần nhất)
Dành cho việc chạy hàng ngày, nhanh chóng và an toàn cho tài khoản Facebook.
```bash
python crawl_3h.py
```

### 2. Chạy chế độ quét sâu (3 ngày gần nhất)
Dành cho việc chạy định kỳ (cuối tuần) để gom lại các bài viết bị bỏ lỡ.
```bash
python crawl_3day.py
```

*Lần đầu chạy, trình duyệt sẽ mở ra và yêu cầu bạn đăng nhập Facebook. Hệ thống sẽ tự động lưu profile vào thư mục `chrome_profile/` cho các lần chạy sau.*

## 📂 Cấu trúc thư mục (Project Structure)

```text
├── src/
│   ├── ai_analyzer.py      # AI pipeline trích xuất hồ sơ ứng viên
│   ├── classifier.py       # Bộ lọc phân loại Ứng viên/Nhà tuyển dụng
│   ├── cookie_manager.py   # Quản lý session Facebook
│   ├── database.py         # Tương tác SQLite (bảng candidates)
│   ├── formatter.py        # Format dữ liệu trước khi đẩy Sheet
│   ├── google_sheets.py    # Đồng bộ Google Sheets
│   ├── job_schema.py       # JSON Schema ép AI trả về đúng cấu trúc
│   ├── ocr.py              # Xử lý ảnh với Tesseract
│   └── rules_engine.py     # Chuẩn hóa dữ liệu bằng rules
├── crawl_3h.py             # Entry point: Quét bài trong 3 giờ
├── crawl_3day.py           # Entry point: Quét bài trong 3 ngày
├── debug_selector.py       # (Tùy chọn) File test selector Facebook
├── groups.txt              # Danh sách URL group Facebook
└── requirements.txt        # Dependencies
```

## 🛠️ Công nghệ sử dụng (Tech Stack)
- **Ngôn ngữ:** Python
- **Crawler:** Selenium WebDriver
- **AI/NLP:** OpenAI API (GPT-3.5/GPT-4) với JSON Schema
- **Computer Vision:** Tesseract OCR, Pillow
- **Database:** SQLite3
- **Cloud Integration:** Google Sheets API

## 🗺️ Lộ trình phát triển (Roadmap)
- [x] Crawler cơ bản với Selenium & Chrome Profile.
- [x] Tích hợp AI trích xuất dữ liệu ứng viên (JSON Schema).
- [x] Xử lý ảnh bằng OCR.
- [x] Bộ lọc phân loại thông minh (loại bỏ đối thủ).
- [x] Lưu trữ SQLite & Google Sheets.
- [ ] Xây dựng Dashboard quản lý ứng viên bằng Streamlit.
- [ ] Xây dựng REST API (FastAPI) để cung cấp dữ liệu.
