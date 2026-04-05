from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient
from PyQt6.QtCore import QTimer
import math


class ArcReactor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        self.setFixedSize(120, 120) 
        self.angle = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # smooth

    def animate(self):
        self.angle += 2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        center_x = w // 2
        center_y = h // 2

        radius = 28

        # 🔥 CORE GLOW
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, QColor("#22d3ee"))
        gradient.setColorAt(1, QColor("#020617"))

        painter.setBrush(gradient)
        painter.setPen(QColor("#22d3ee"))

        painter.drawEllipse(
            center_x - radius // 2,
            center_y - radius // 2,
            radius,
            radius
        )

        # 🔵 OUTER RING
        pen = QPen(QColor("#6d7070"), 4)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 0))

        outer_radius = radius + 15

        painter.drawEllipse(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )

        # 🌀 ROTATING ARC
        arc_pen = QPen(QColor("#06b6d4"), 6)
        painter.setPen(arc_pen)

        painter.drawArc(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2,
            self.angle * 16,
            120 * 16
        )

        # 🔥 SECOND ARC (opposite)
        painter.drawArc(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2,
            (self.angle + 180) * 16,
            90 * 16
        )