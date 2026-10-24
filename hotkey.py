"""Phần 2 - Phím tắt toàn hệ thống bằng Windows API RegisterHotKey."""
import ctypes, threading
from ctypes import wintypes
from PySide6.QtCore import QThread, Signal

MODS = {"alt": 0x1, "ctrl": 0x2, "shift": 0x4, "meta": 0x8, "win": 0x8}
WM_HOTKEY, WM_QUIT, MOD_NOREPEAT = 0x0312, 0x0012, 0x4000


def parse(text):
    """'Ctrl+Shift+T' -> (modifiers, virtual-key). Ném ValueError nếu không hợp lệ."""
    parts = [p.strip().lower() for p in text.split("+") if p.strip()]
    if len(parts) < 2:
        raise ValueError("Cần ít nhất một phím bổ trợ (Ctrl/Alt/Shift) và một phím chính.")
    mods = 0
    for p in parts[:-1]:
        if p not in MODS:
            raise ValueError(f"Phím bổ trợ không hợp lệ: {p}")
        mods |= MODS[p]
    k = parts[-1]
    if len(k) == 1 and k.isalnum():
        vk = ord(k.upper())
    elif k[0] == "f" and k[1:].isdigit() and 1 <= int(k[1:]) <= 12:
        vk = 0x70 + int(k[1:]) - 1
    else:
        raise ValueError(f"Phím chính không được hỗ trợ: {k}")
    return mods | MOD_NOREPEAT, vk


class HotkeyListener(QThread):
    pressed = Signal()

    def __init__(self, mods, vk):
        super().__init__()
        self.mods, self.vk = mods, vk
        self.ready, self.error, self.tid = threading.Event(), None, None

    def run(self):
        u32 = ctypes.windll.user32
        msg = wintypes.MSG()
        u32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)  # tạo hàng đợi message
        self.tid = ctypes.windll.kernel32.GetCurrentThreadId()
        if not u32.RegisterHotKey(None, 1, self.mods, self.vk):
            self.error = "Tổ hợp phím đã bị ứng dụng khác sử dụng hoặc không hợp lệ."
            self.ready.set()
            return
        self.ready.set()
        while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                self.pressed.emit()
        u32.UnregisterHotKey(None, 1)

    def stop(self):
        if self.tid:
            ctypes.windll.user32.PostThreadMessageW(self.tid, WM_QUIT, 0, 0)
        self.wait(2000)


def start_listener(text):
    """Đăng ký phím tắt; ném ValueError/RuntimeError nếu lỗi hoặc trùng."""
    mods, vk = parse(text)
    listener = HotkeyListener(mods, vk)
    listener.start()
    listener.ready.wait(3)
    if listener.error:
        listener.wait()
        raise RuntimeError(listener.error)
    return listener
