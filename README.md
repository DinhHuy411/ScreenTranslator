# Screen Translator

Nhấn phím tắt -> kéo chọn vùng màn hình -> OCR -> dịch sang tiếng Việt -> hiện kết quả.

## Cài đặt (Windows)
1. Cài Python 3.10+.
2. Cài Tesseract OCR (bản UB Mannheim) và tick thêm gói ngôn ngữ: Japanese, Korean, Chinese (Simplified).
   Mặc định tại `C:\Program Files\Tesseract-OCR\tesseract.exe` (đổi trong file `.screen_translator.json` ở thư mục người dùng nếu khác).
3. `pip install -r requirements.txt`
4. `python main.py`

## Cấu trúc (mỗi file là một phần)
| File | Chức năng đề bài |
|---|---|
| config.py | F01, F02 - lưu cấu hình JSON |
| hotkey.py | F01, F09 - phím tắt toàn hệ thống, báo trùng/không hợp lệ |
| selector.py | F03, F04 - lớp phủ chọn vùng, Esc để hủy, đa màn hình |
| ocr.py | F05 - Tesseract |
| translator.py | F06 - dịch tách riêng khỏi OCR, xử lý lỗi mạng |
| ui.py | F07, F08 - màn hình Cài đặt và Kết quả (Sao chép / Dịch lại / Đóng) |
| main.py | Ghép toàn bộ, chạy OCR+dịch ở luồng nền (không treo), khay hệ thống |
