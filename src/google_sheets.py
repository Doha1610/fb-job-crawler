import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from src.formatter import format_post_full

# ===== CẤU HÌNH =====
CREDS_FILE = "google_credentials.json"
SPREADSHEET_ID = "1FX0JOUwtr3g7seYlz2-_5GrmIcLCWSCA0Mzo6aP-Eck"
SHEET_NAME = "Jobs"
# ====================


def get_sheets_service():
    """Khởi tạo Google Sheets service"""
    if not os.path.exists(CREDS_FILE):
        raise FileNotFoundError(f"❌ Không tìm thấy file: {CREDS_FILE}")

    creds = service_account.Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    return service


def push_posts_to_sheet(posts: list) -> bool:
    """Đẩy danh sách bài viết lên Google Sheet."""
    if not posts:
        print("⚠️ Không có bài nào để đẩy lên Sheet")
        return False

    try:
        service = get_sheets_service()
        rows = [format_post_full(post) for post in posts]

        body = {'values': rows}
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A2',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        updated = result.get('updates', {}).get('updatedCells', 0)
        print(f"✅ Đã đẩy {len(rows)} bài lên Google Sheet ({updated} cells)")
        return True

    except Exception as e:
        print(f"❌ Lỗi đẩy Sheet: {e}")
        return False