"""Phần 7 - Ghép các module thành ứng dụng hoàn chỉnh.
Luồng: phím tắt -> chọn vùng -> chụp -> OCR -> dịch -> hiển thị kết quả."""
import sys, os, ctypes
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
import config, hotkey, ocr, translator
from selector import Overlay
from ui import SettingsWindow, ResultWindow


ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")


class Worker(QThread):
    """Chạy OCR/dịch ở luồng nền để giao diện không bị treo."""
    done = Signal(str, str)
    failed = Signal(str)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            self.done.emit(*self.fn())
        except Exception as e:
            self.failed.emit(str(e))


class Controller(QObject):
    def __init__(self, app):
        super().__init__()
        self.app, self.cfg = app, config.load()
        self.listener = self.worker = None
        self.overlays = []
        self.settings, self.result = SettingsWindow(self.cfg), ResultWindow()
        self.settings.saveRequested.connect(self.on_save)
        self.settings.toggleRequested.connect(self.on_toggle)
        self.result.retranslate.connect(self.on_retranslate)

        self.tray = QSystemTrayIcon(QIcon(ICON), app)
        menu = QMenu()
        menu.addAction("Mở cài đặt", self.settings.show)
        menu.addAction("Thoát", self.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()
        app.aboutToQuit.connect(self.disable)

        if self.cfg["hotkey_enabled"]:
            self.enable()
        self.settings.set_status(self.listener is not None)
        self.settings.show()

    # ----- phím tắt -----
    def enable(self, hk=None):
        try:
            self.listener = hotkey.start_listener(hk or self.cfg["hotkey"])
            self.listener.pressed.connect(self.begin_capture)
            return True
        except (ValueError, RuntimeError) as e:
            self.listener = None
            QMessageBox.warning(self.settings, "Phím tắt", str(e))
            return False

    def disable(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

    def on_toggle(self):
        if self.listener:
            self.disable()
        else:
            self.enable()
        self.cfg["hotkey_enabled"] = self.listener is not None
        config.save(self.cfg)
        self.settings.set_status(self.listener is not None)

    def on_save(self, hk, lang):
        try:
            hotkey.parse(hk)
        except ValueError as e:
            QMessageBox.warning(self.settings, "Phím tắt không hợp lệ", str(e))
            return
        old, was_on = self.cfg["hotkey"], self.listener is not None
        if was_on:
            self.disable()
            if not self.enable(hk):          # trùng phím -> khôi phục phím cũ
                self.enable(old)
                self.settings.set_hotkey(old)
                self.settings.set_status(self.listener is not None)
                return
        self.cfg.update(hotkey=hk, source_lang=lang)
        config.save(self.cfg)
        self.settings.set_status(self.listener is not None)
        QMessageBox.information(self.settings, "Screen Translator", "Đã lưu cấu hình.")

    # ----- quy trình dịch -----
    def begin_capture(self):
        if self.overlays or (self.worker and self.worker.isRunning()):
            return
        self.result.hide()
        self.app.processEvents()
        self.overlays = [Overlay(s) for s in self.app.screens()]
        for o in self.overlays:
            o.selected.connect(self.on_selected)
            o.cancelled.connect(self.close_overlays)
            o.show(); o.activateWindow()

    def close_overlays(self):
        for o in self.overlays:
            o.close()
        self.overlays = []

    def run_worker(self, fn):
        self.result.set_busy(True)
        self.result.show()
        self.worker = Worker(fn)
        self.worker.done.connect(self.result.show_result)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_selected(self, pix):
        self.close_overlays()
        src = self.cfg["source_lang"]

        def job():
            text = ocr.recognize(pix, config.tesseract_lang(src), self.cfg["tesseract_path"])
            if not text:
                raise RuntimeError("Không tìm thấy văn bản trong vùng đã chọn.")
            return text, translator.translate(text, src)
        self.run_worker(job)

    def on_retranslate(self, text):
        text = text.strip()
        if not text:
            QMessageBox.warning(self.result, "Dịch lại", "Chưa có văn bản để dịch.")
            return
        self.run_worker(lambda: (text, translator.translate(text, self.cfg["source_lang"])))

    def on_failed(self, msg):
        self.result.hide()
        QMessageBox.warning(None, "Screen Translator", msg)

    def quit(self):
        self.disable()
        self.app.quit()


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ScreenTranslator.App")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON))
    app.setQuitOnLastWindowClosed(False)
    ctrl = Controller(app)
    sys.exit(app.exec())
