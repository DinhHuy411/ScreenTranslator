"""Phần 3 - Lớp phủ chọn vùng màn hình và chụp ảnh vùng chọn (hỗ trợ nhiều màn hình)."""
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget


class Overlay(QWidget):
    selected = Signal(object)   # QPixmap của vùng đã chọn
    cancelled = Signal()

    def __init__(self, screen):
        super().__init__()
        self.shot = screen.grabWindow(0)  # chụp trước khi hiện lớp phủ
        self.setScreen(screen)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setGeometry(screen.geometry())
        self.setCursor(Qt.CrossCursor)
        self.start = self.end = None

    def _src(self, r):
        s = self.shot.width() / max(self.width(), 1)  # hệ số DPI
        return QRect(int(r.x() * s), int(r.y() * s), int(r.width() * s), int(r.height() * s))

    def paintEvent(self, _):
        p = QPainter(self)
        p.drawPixmap(self.rect(), self.shot)
        p.fillRect(self.rect(), QColor(0, 0, 0, 110))
        if self.start:
            r = QRect(self.start, self.end).normalized()
            p.drawPixmap(r, self.shot, self._src(r))  # làm sáng vùng chọn
            p.setPen(QPen(QColor(0, 170, 255), 2))
            p.drawRect(r)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.start = self.end = e.position().toPoint()
            self.update()

    def mouseMoveEvent(self, e):
        if self.start:
            self.end = e.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or not self.start:
            return
        r = QRect(self.start, e.position().toPoint()).normalized()
        self.start = None
        if r.width() < 5 or r.height() < 5:
            self.update()
            return
        self.selected.emit(self.shot.copy(self._src(r)))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.cancelled.emit()
