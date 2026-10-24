"""Phần 1 - Quản lý cấu hình người dùng (lưu JSON)."""
import json, os

PATH = os.path.join(os.path.expanduser("~"), ".screen_translator.json")
DEFAULT = {
    "hotkey": "Ctrl+Shift+T",
    "source_lang": "auto",
    "hotkey_enabled": True,
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
}
# Tên hiển thị -> (mã dịch, mã Tesseract)
LANGS = {
    "Tự động nhận diện": ("auto", "eng+jpn+kor+chi_sim"),
    "Tiếng Anh": ("en", "eng"),
    "Tiếng Nhật": ("ja", "jpn"),
    "Tiếng Hàn": ("ko", "kor"),
    "Tiếng Trung": ("zh-CN", "chi_sim"),
}


def tesseract_lang(code):
    return next((t for c, t in LANGS.values() if c == code), "eng")


def load():
    cfg = dict(DEFAULT)
    try:
        with open(PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


def save(cfg):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
