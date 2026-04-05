from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import QTimer
import math


class AuraRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)

        self.angle = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # smooth 60 FPS

    def animate(self):
        parent = self.parent()

        if parent and getattr(parent, "is_listening", False):
            color = "#22d3ee"
            self.angle += 8   # 🔥 fast

        elif parent and getattr(parent, "is_speaking", False):
            color = "#a78bfa"
            self.angle += 3   # 🤖 medium

        else:
            color = "#1e293b"
            self.angle += 0.5   # 🔥 slow idle rotation (IMPORTANT)

        self.update()   # 🔥 ALWAYS update

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        size = min(w, h) - 120

        rect_x = (w - size) // 2
        rect_y = (h - size) // 2

        # base circle
        pen_bg = QPen(QColor("#1e293b"), 8)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect_x, rect_y, size, size)

        # animated arc
        pen = QPen(QColor("#22d3ee"), 8)
        painter.setPen(pen)

        span_angle = 120 * 16  # arc size

        painter.drawArc(
            rect_x,
            rect_y,
            size,
            size,
            int(self.angle * 16),
            span_angle
        )