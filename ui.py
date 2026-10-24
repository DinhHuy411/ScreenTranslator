"""Phần 6 - Giao diện: màn hình Cài đặt và màn hình Kết quả dịch."""
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (QWidget, QLabel, QComboBox, QPushButton, QFormLayout, QVBoxLayout,
                               QHBoxLayout, QKeySequenceEdit, QPlainTextEdit, QApplication)
import config


class SettingsWindow(QWidget):
    saveRequested = Signal(str, str)   # hotkey, mã ngôn ngữ nguồn
    toggleRequested = Signal()

    def __init__(self, cfg):
        super().__init__()
        self.setWindowTitle("Screen Translator - Cài đặt")
        self.setMinimumWidth(380)
        self.status = QLabel()
        self.key = QKeySequenceEdit(QKeySequence(cfg["hotkey"]))
        self.key.setMaximumSequenceLength(1)
        self.lang = QComboBox()
        for name, (code, _) in config.LANGS.items():
            self.lang.addItem(name, code)
        self.lang.setCurrentIndex(max(self.lang.findData(cfg["source_lang"]), 0))
        self.toggle, save = QPushButton(), QPushButton("Lưu cấu hình")
        self.toggle.clicked.connect(self.toggleRequested)
        save.clicked.connect(lambda: self.saveRequested.emit(
            self.key.keySequence().toString(QKeySequence.PortableText), self.lang.currentData()))
        form = QFormLayout(self)
        title = QLabel("<h2>Screen Translator</h2>")
        form.addRow(title)
        form.addRow("Trạng thái:", self.status)
        form.addRow("Phím tắt:", self.key)
        form.addRow("Ngôn ngữ nguồn:", self.lang)
        form.addRow("Ngôn ngữ đích:", QLabel("Tiếng Việt"))
        form.addRow(self.toggle)
        form.addRow(save)

    def set_status(self, enabled):
        self.status.setText("<span style='color:green'>● Đang hoạt động</span>" if enabled
                            else "<span style='color:gray'>○ Đã tắt</span>")
        self.toggle.setText("Tắt phím tắt" if enabled else "Bật phím tắt")

    def set_hotkey(self, text):
        self.key.setKeySequence(QKeySequence(text))

    def closeEvent(self, e):  # thu nhỏ xuống khay thay vì thoát
        e.ignore()
        self.hide()


class ResultWindow(QWidget):
    retranslate = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kết quả dịch")
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.resize(480, 380)
        self.orig, self.trans = QPlainTextEdit(), QPlainTextEdit()
        self.trans.setReadOnly(True)
        self.btn_copy, self.btn_re, btn_close = (QPushButton("Sao chép"), QPushButton("Dịch lại"),
                                                 QPushButton("Đóng"))
        self.btn_copy.clicked.connect(self._copy)
        self.btn_re.clicked.connect(lambda: self.retranslate.emit(self.orig.toPlainText()))
        btn_close.clicked.connect(self.hide)
        row = QHBoxLayout()
        for b in (self.btn_copy, self.btn_re, btn_close):
            row.addWidget(b)
        lay = QVBoxLayout(self)
        for w in (QLabel("Văn bản nhận diện (có thể sửa):"), self.orig,
                  QLabel("Bản dịch tiếng Việt:"), self.trans):
            lay.addWidget(w)
        lay.addLayout(row)

    def set_busy(self, busy):
        for b in (self.btn_copy, self.btn_re):
            b.setEnabled(not busy)
        if busy:
            self.trans.setPlainText("Đang nhận diện và dịch...")

    def show_result(self, orig, trans):
        self.orig.setPlainText(orig)
        self.trans.setPlainText(trans)
        self.set_busy(False)
        self.show(); self.raise_(); self.activateWindow()

    def _copy(self):
        QApplication.clipboard().setText(self.trans.toPlainText())
        self.btn_copy.setText("Đã sao chép ✓")
        QTimer.singleShot(1200, lambda: self.btn_copy.setText("Sao chép"))
