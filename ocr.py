"""Phần 4 - Nhận diện văn bản bằng Tesseract OCR."""
import io
import pytesseract
from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice


def _to_pil(pix):
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    pix.save(buf, "PNG")
    return Image.open(io.BytesIO(bytes(buf.data())))


def recognize(pix, lang, tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    img = _to_pil(pix).convert("L")
    if img.height < 200:  # phóng to vùng nhỏ để OCR chính xác hơn
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    try:
        text = pytesseract.image_to_string(img, lang=lang)
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("Không tìm thấy Tesseract OCR. Hãy cài đặt và kiểm tra đường dẫn.")
    except pytesseract.TesseractError as e:
        raise RuntimeError(f"Lỗi OCR (có thể thiếu gói ngôn ngữ '{lang}'): {e}")
    return "\n".join(l.strip() for l in text.splitlines() if l.strip())
