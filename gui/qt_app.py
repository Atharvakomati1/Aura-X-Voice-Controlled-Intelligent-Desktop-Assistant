import sys
import math
import re
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QPoint, pyqtProperty, QSequentialAnimationGroup
)
from PyQt6.QtGui import (
    QTextCursor, QColor, QPainter, QPen, QBrush,
    QLinearGradient, QRadialGradient, QFont, QFontDatabase,
    QPainterPath, QConicalGradient
)


# ─────────────────────────────────────────────
#  SENTENCE SPLITTER
# ─────────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    """
    Split response into natural spoken sentences.
    Keeps punctuation attached so TTS sounds natural.
    """
    # Split on . ! ? but not on abbreviations like "A.I." or "e.g."
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    # Merge very short fragments (< 4 words) with the next sentence
    merged = []
    carry = ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        carry = (carry + " " + p).strip() if carry else p
        if len(carry.split()) >= 4:
            merged.append(carry)
            carry = ""
    if carry:
        merged.append(carry)
    return merged if merged else [text]


# ─────────────────────────────────────────────
#  WORKERS
# ─────────────────────────────────────────────

class VoiceWorker(QThread):
    finished = pyqtSignal(str)

    def run(self):
        from services.speech_to_text import listen
        command = ""
        for _ in range(3):
            command = listen(verbose=True)
            if command:
                break
        self.finished.emit(command)


class AIWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        from core.brain import process_command
        result = process_command(self.text)
        self.finished.emit(result)


class SentenceSpeaker(QThread):
    """
    Speaks a single sentence in a background thread.
    Emits `done` when TTS finishes so the next sentence can begin.
    """
    done = pyqtSignal()

    def __init__(self, sentence: str):
        super().__init__()
        self.sentence = sentence

    def run(self):
        try:
            from services.text_to_speech import speak
            speak(self.sentence)
        except Exception as e:
            print(f"[TTS] {e}")
        finally:
            self.done.emit()


# ─────────────────────────────────────────────
#  ORBS & VISUAL WIDGETS
# ─────────────────────────────────────────────

class NeuralOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self._state = "idle"
        self._angle1 = 0
        self._angle2 = 45
        self._angle3 = 90
        self._pulse = 0.0
        self._pulse_dir = 1
        self._particles = [
            {"a": i * 40, "r": 72 + (i % 3) * 8, "size": 2 + (i % 3)}
            for i in range(9)
        ]
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._tick)
        self.anim_timer.start(16)

    def set_state(self, state: str):
        self._state = state
        self.update()

    def _tick(self):
        speeds = {"idle": 0.4, "listening": 1.1, "thinking": 1.8, "speaking": 1.4}
        sp = speeds.get(self._state, 0.4)
        self._angle1 = (self._angle1 + sp) % 360
        self._angle2 = (self._angle2 - sp * 0.7) % 360
        self._angle3 = (self._angle3 + sp * 1.3) % 360
        self._pulse += 0.02 * sp * self._pulse_dir
        if self._pulse >= 1.0:
            self._pulse_dir = -1
        elif self._pulse <= 0.0:
            self._pulse_dir = 1
        for p in self._particles:
            p["a"] = (p["a"] + sp * 0.5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        state_colors = {
            "idle":      ("#0ea5e9", "#22d3ee", "#7dd3fc"),
            "listening": ("#22c55e", "#4ade80", "#86efac"),
            "thinking":  ("#f59e0b", "#fbbf24", "#fde68a"),
            "speaking":  ("#a855f7", "#c084fc", "#e9d5ff"),
        }
        c1, c2, c3 = state_colors.get(self._state, state_colors["idle"])

        for i in range(5, 0, -1):
            r = 88 + i * 4 + self._pulse * 6
            alpha = int(18 - i * 2)
            grad = QRadialGradient(cx, cy, r)
            col = QColor(c1); col.setAlpha(alpha)
            grad.setColorAt(0, col)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        def draw_ring(angle, radius, color_hex, alpha):
            c = QColor(color_hex); c.setAlpha(alpha)
            pen = QPen(c, 1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(angle)
            painter.drawEllipse(int(-radius), int(-radius * 0.35),
                                int(radius * 2), int(radius * 0.7))
            painter.restore()

        draw_ring(self._angle1, 74, c1, 180)
        draw_ring(self._angle2, 68, c2, 140)
        draw_ring(self._angle3, 62, c3, 100)

        core_r = 46 + self._pulse * 4
        core_grad = QRadialGradient(cx - 12, cy - 12, core_r)
        core_grad.setColorAt(0.0, QColor(c3))
        core_grad.setColorAt(0.4, QColor(c1))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 200))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - core_r), int(cy - core_r),
                            int(core_r * 2), int(core_r * 2))

        hl_r = 16
        hl_grad = QRadialGradient(cx - 14, cy - 16, hl_r)
        hl_grad.setColorAt(0, QColor(255, 255, 255, 130))
        hl_grad.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(hl_grad))
        painter.drawEllipse(int(cx - 14 - hl_r), int(cy - 16 - hl_r),
                            int(hl_r * 2), int(hl_r * 2))

        for p in self._particles:
            rad = math.radians(p["a"])
            px = cx + math.cos(rad) * p["r"]
            py = cy + math.sin(rad) * p["r"] * 0.4
            dot = QColor(c2); dot.setAlpha(200)
            painter.setBrush(QBrush(dot))
            painter.setPen(Qt.PenStyle.NoPen)
            s = p["size"]
            painter.drawEllipse(int(px - s), int(py - s), s * 2, s * 2)

        painter.end()


class WaveformBar(QWidget):
    def __init__(self, parent=None, bar_count=12):
        super().__init__(parent)
        self.setFixedSize(80, 28)
        self._heights = [0.2] * bar_count
        self._targets = [0.2] * bar_count
        self._active = False
        self._color = "#22d3ee"
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(60)

    def set_active(self, active: bool, color="#22d3ee"):
        self._active = active
        self._color = color

    def _tick(self):
        import random
        if self._active:
            self._targets = [random.uniform(0.2, 1.0) for _ in self._heights]
        else:
            self._targets = [0.15] * len(self._heights)
        for i in range(len(self._heights)):
            self._heights[i] += (self._targets[i] - self._heights[i]) * 0.35
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        n = len(self._heights)
        w, h = self.width(), self.height()
        bar_w = max(2, w // n - 2)
        spacing = (w - bar_w * n) // (n + 1)
        color = QColor(self._color)
        for i, bh in enumerate(self._heights):
            bh_px = int(bh * (h - 4))
            x = spacing + i * (bar_w + spacing)
            y = h - bh_px - 2
            grad = QLinearGradient(x, y, x, h)
            top = QColor(color); top.setAlpha(220)
            bot = QColor(color); bot.setAlpha(60)
            grad.setColorAt(0, top); grad.setColorAt(1, bot)
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bh_px, 1, 1)
        painter.end()


class ChatDisplay(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #e2e8f0;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                padding: 8px 4px;
                border: none;
                selection-background-color: #0ea5e940;
            }
        """)
        self.document().setDocumentMargin(4)

    def append_user(self, text):
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertHtml(
            f"<div style='margin:6px 0;'>"
            f"<span style='color:#60a5fa;font-family:Courier New;font-weight:700;"
            f"font-size:11px;letter-spacing:2px;'>YOU ▸</span>"
            f"<span style='color:#cbd5e1;font-family:Courier New;font-size:13px;'> {text}</span>"
            f"</div><br/>"
        )
        self._scroll()

    def append_aura_label(self):
        """Insert the AURA-X prefix — plain text will be appended after this."""
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertHtml(
            f"<span style='color:#22d3ee;font-family:Courier New;font-weight:700;"
            f"font-size:11px;letter-spacing:2px;'>AURA&#8209;X ▸</span>"
            f"<span style='color:#e2e8f0;font-family:Courier New;font-size:13px;'> </span>"
        )
        self._scroll()

    def append_system(self, text):
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertHtml(
            f"<div style='margin:4px 0;'>"
            f"<span style='color:#475569;font-family:Courier New;font-size:11px;"
            f"font-style:italic;'>◆ {text}</span>"
            f"</div><br/>"
        )
        self._scroll()

    def _scroll(self):
        QTimer.singleShot(10, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()))


class GlowButton(QPushButton):
    def __init__(self, text, accent="#22d3ee", parent=None):
        super().__init__(text, parent)
        self._accent = accent
        self.setFixedHeight(40)
        self._apply_style(False)

    def _apply_style(self, hovered):
        bg = self._accent if hovered else "transparent"
        fg = "#000" if hovered else self._accent
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {self._accent};
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
                padding: 0 16px;
            }}
        """)

    def enterEvent(self, e):
        self._apply_style(True)
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(20)
        effect.setColor(QColor(self._accent))
        effect.setOffset(0, 0)
        self.setGraphicsEffect(effect)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._apply_style(False)
        self.setGraphicsEffect(None)
        super().leaveEvent(e)


class VoicePulseButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(54, 54)
        self._pulse = 0.0
        self._pulse_dir = 1
        self._active = False
        self._hovered = False
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(20)

    def set_active(self, val):
        self._active = val
        self.update()

    def _tick(self):
        if self._active or self._hovered:
            self._pulse += 0.04 * self._pulse_dir
            if self._pulse >= 1: self._pulse_dir = -1
            elif self._pulse <= 0: self._pulse_dir = 1
        else:
            self._pulse = max(0.0, self._pulse - 0.05)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        color = "#22c55e" if self._active else "#22d3ee"
        if self._pulse > 0:
            pr = 24 + self._pulse * 10
            c = QColor(color); c.setAlpha(int(80 * self._pulse))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(c, 1))
            painter.drawEllipse(int(cx - pr), int(cy - pr), int(pr * 2), int(pr * 2))
        r = 22
        grad = QRadialGradient(cx - 5, cy - 5, r)
        grad.setColorAt(0, QColor(color).lighter(130))
        grad.setColorAt(1, QColor(color).darker(160))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
        painter.setPen(QPen(QColor("#000"), 2))
        painter.drawRoundedRect(int(cx - 5), int(cy - 10), 10, 14, 5, 5)
        painter.drawArc(int(cx - 8), int(cy - 1), 16, 12, 0, -180 * 16)
        painter.drawLine(int(cx), int(cy + 10), int(cx), int(cy + 14))
        painter.drawLine(int(cx - 4), int(cy + 14), int(cx + 4), int(cy + 14))
        painter.end()

    def mousePressEvent(self, e): self.clicked.emit()
    def enterEvent(self, e): self._hovered = True
    def leaveEvent(self, e): self._hovered = False


class StatusStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        self._dot = QLabel("●"); self._dot.setFixedWidth(14)
        layout.addWidget(self._dot)
        self._label = QLabel("IDLE"); self._label.setFont(QFont("Courier New", 10))
        layout.addWidget(self._label)
        self._wave = WaveformBar(self)
        layout.addWidget(self._wave)
        layout.addStretch()
        self._info = QLabel("")
        self._info.setFont(QFont("Courier New", 9))
        self._info.setStyleSheet("color: #475569;")
        layout.addWidget(self._info)
        self.setStyleSheet("background-color: #0a0f1e; border-top: 1px solid #1e293b;")
        self.set_state("idle")

    def set_state(self, state: str, info=""):
        configs = {
            "idle":      ("#475569", "IDLE",       False, "#475569"),
            "listening": ("#22c55e", "LISTENING",  True,  "#22c55e"),
            "thinking":  ("#f59e0b", "THINKING",   True,  "#f59e0b"),
            "speaking":  ("#a855f7", "SPEAKING",   True,  "#a855f7"),
            "responding":("#22d3ee", "RESPONDING", True,  "#22d3ee"),
            "error":     ("#ef4444", "ERROR",       False, "#ef4444"),
        }
        color, label, wave_on, wave_color = configs.get(state, configs["idle"])
        self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        self._label.setStyleSheet(
            f"color: {color}; font-family: 'Courier New'; font-size: 10px; "
            f"letter-spacing: 2px; font-weight: bold;")
        self._label.setText(label)
        self._wave.set_active(wave_on, wave_color)
        self._info.setText(info)


class InfoCard(QFrame):
    def __init__(self, title, value, color="#22d3ee", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0a0f1e;
                border: 1px solid {color}30;
                border-left: 3px solid {color};
                border-radius: 6px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(f"color: {color}80; font-family: 'Courier New'; font-size: 9px; letter-spacing: 2px;")
        lay.addWidget(t)
        self.val_label = QLabel(value)
        self.val_label.setStyleSheet(
            f"color: {color}; font-family: 'Courier New'; font-size: 12px; font-weight: bold;")
        lay.addWidget(self.val_label)

    def set_value(self, v): self.val_label.setText(v)


# ─────────────────────────────────────────────
#  STREAMING RESPONSE ENGINE
#  Handles sentence-by-sentence type + speak
# ─────────────────────────────────────────────

class StreamingResponseEngine:
    """
    Given a full response string, splits into sentences then for each sentence:
      1. Types it character-by-character into the chat (via Qt main thread)
      2. Simultaneously speaks it via SentenceSpeaker (background thread)
      3. After both finish, moves to the next sentence

    The typing speed is calibrated so it finishes ~slightly before or
    simultaneously with the TTS, making them feel in sync.
    """

    CHAR_INTERVAL_MS = 18   # ms per character typed — tweak to match your TTS speed

    def __init__(self, response: str, chat: ChatDisplay,
                 on_state_change, on_all_done):
        self.sentences   = split_sentences(response)
        self.chat        = chat
        self._set_state  = on_state_change   # callable(state_str)
        self._on_done    = on_all_done        # callable() — fires when all done

        self._sent_idx   = 0      # which sentence we're on
        self._char_idx   = 0      # which char within current sentence
        self._cur_sent   = ""
        self._type_timer = None
        self._tts_done   = False
        self._type_done  = False
        self._speaker    = None

        # Insert AURA-X label once for the whole response
        self.chat.append_aura_label()

    def start(self):
        self._next_sentence()

    def _next_sentence(self):
        if getattr(self, "_stopped", False):
            return
        if self._sent_idx >= len(self.sentences):
            # All done
            self.chat.moveCursor(QTextCursor.MoveOperation.End)
            self.chat.insertHtml("<br/>")
            self._set_state("idle")
            self._on_done()
            return

        self._cur_sent  = self.sentences[self._sent_idx]
        self._char_idx  = 0
        self._tts_done  = False
        self._type_done = False
        self._sent_idx += 1

        # ── Start TTS for this sentence ──────────────────────
        self._speaker = SentenceSpeaker(self._cur_sent)
        self._speaker.done.connect(self._on_tts_done)
        self._speaker.start()

        # ── Start typing for this sentence ───────────────────
        self._type_timer = QTimer()
        self._type_timer.timeout.connect(self._type_tick)
        self._type_timer.start(self.CHAR_INTERVAL_MS)

    def _type_tick(self):
        if self._char_idx < len(self._cur_sent):
            ch = self._cur_sent[self._char_idx]
            self._char_idx += 1
            self.chat.moveCursor(QTextCursor.MoveOperation.End)
            self.chat.insertPlainText(ch)
            self.chat.verticalScrollBar().setValue(
                self.chat.verticalScrollBar().maximum())
        else:
            # Typing finished for this sentence
            self._type_timer.stop()
            self._type_timer = None
            # Add a space between sentences in the chat
            self.chat.moveCursor(QTextCursor.MoveOperation.End)
            self.chat.insertPlainText(" ")
            self._type_done = True
            self._check_advance()

    def _on_tts_done(self):
        self._tts_done = True
        self._check_advance()

    def _check_advance(self):
        """Move to the next sentence only when BOTH typing and TTS are done."""
        if getattr(self, "_stopped", False):
            return
        if self._tts_done and self._type_done:
            # Small gap between sentences (feels natural)
            QTimer.singleShot(120, self._next_sentence)

    def stop(self):
        """Cancel everything immediately."""
        self._stopped = True          # guard so pending QTimer callbacks no-op
        if self._type_timer:
            self._type_timer.stop()
            self._type_timer = None
        if self._speaker and self._speaker.isRunning():
            self._speaker.terminate()


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────

class AuraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AURA-X  //  NEURAL INTERFACE v2.0")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet("background-color: #060c1a;")

        self.is_listening  = False
        self.is_speaking   = False
        self._msg_count    = 0
        self._stream_engine: StreamingResponseEngine | None = None

        self._build_ui()
        self._start_clock()
        QTimer.singleShot(400, self._send_greeting)

    # ─── UI CONSTRUCTION ───────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._make_left_panel())
        root.addWidget(self._make_center_panel(), 1)
        root.addWidget(self._make_right_panel())

    def _make_left_panel(self):
        panel = QFrame()
        panel.setFixedWidth(210)
        panel.setStyleSheet("""
            QFrame { background-color: #07101f; border-right: 1px solid #0f2040; }
        """)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(16, 20, 16, 20)
        lay.setSpacing(14)

        logo = QLabel("AURA&#8209;X")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("""
            color: #22d3ee; font-family: 'Courier New', monospace;
            font-size: 20px; font-weight: bold; letter-spacing: 4px; padding: 10px 0;
        """)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(24); glow.setColor(QColor("#22d3ee")); glow.setOffset(0, 0)
        logo.setGraphicsEffect(glow)
        lay.addWidget(logo)

        sub = QLabel("NEURAL INTERFACE")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: #1e4060; font-family: 'Courier New'; font-size: 8px; letter-spacing: 3px;")
        lay.addWidget(sub)

        lay.addWidget(self._divider())

        self.orb = NeuralOrb(self)
        lay.addWidget(self.orb, 0, Qt.AlignmentFlag.AlignHCenter)

        self._orb_label = QLabel("● IDLE")
        self._orb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._orb_label.setStyleSheet(
            "color: #475569; font-family: 'Courier New'; font-size: 9px; letter-spacing: 2px;")
        lay.addWidget(self._orb_label)

        lay.addWidget(self._divider())

        ctrl = QLabel("CONTROLS")
        ctrl.setStyleSheet("color: #1e4060; font-family: 'Courier New'; font-size: 8px; letter-spacing: 3px;")
        lay.addWidget(ctrl)

        voice_row = QHBoxLayout()
        voice_row.setSpacing(10)
        self._voice_btn = VoicePulseButton(self)
        self._voice_btn.clicked.connect(self._handle_voice)
        voice_row.addWidget(self._voice_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        voice_lbl = QLabel("VOICE INPUT\nPress to speak")
        voice_lbl.setStyleSheet("color: #64748b; font-family: 'Courier New'; font-size: 10px;")
        voice_row.addWidget(voice_lbl)
        lay.addLayout(voice_row)

        clr_btn = GlowButton("CLEAR CHAT", "#ef4444")
        clr_btn.clicked.connect(self._clear_chat)
        lay.addWidget(clr_btn)

        lay.addStretch()

        credit = QLabel("v2.0  //  AURA SYSTEMS")
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit.setStyleSheet("color: #1e3050; font-family: 'Courier New'; font-size: 8px; letter-spacing: 2px;")
        lay.addWidget(credit)
        return panel

    def _make_center_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background-color: #060c1a;")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(48)
        header.setStyleSheet("background-color: #07101f; border-bottom: 1px solid #0f2040;")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(20, 0, 20, 0)
        h_title = QLabel("SECURE NEURAL TERMINAL  //  ENCRYPTED")
        h_title.setStyleSheet("color: #1e4060; font-family: 'Courier New'; font-size: 10px; letter-spacing: 2px;")
        hlay.addWidget(h_title)
        hlay.addStretch()
        self._clock_label = QLabel("--:--:--")
        self._clock_label.setStyleSheet(
            "color: #22d3ee; font-family: 'Courier New'; font-size: 11px; letter-spacing: 1px;")
        hlay.addWidget(self._clock_label)
        lay.addWidget(header)

        chat_container = QFrame()
        chat_container.setStyleSheet("QFrame { background-color: #060c1a; }")
        clayout = QVBoxLayout(chat_container)
        clayout.setContentsMargins(16, 16, 16, 8)
        self._chat = ChatDisplay()
        clayout.addWidget(self._chat)
        lay.addWidget(chat_container, 1)

        self._status = StatusStrip()
        lay.addWidget(self._status)

        input_bar = QFrame()
        input_bar.setFixedHeight(68)
        input_bar.setStyleSheet("background-color: #07101f; border-top: 1px solid #0f2040;")
        ilay = QHBoxLayout(input_bar)
        ilay.setContentsMargins(16, 12, 16, 12)
        ilay.setSpacing(10)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter command or query  ...")
        self._input.setStyleSheet("""
            QLineEdit {
                background-color: #0a1628; color: #e2e8f0;
                border: 1px solid #1e3a5f; border-radius: 6px;
                font-family: 'Courier New', monospace; font-size: 13px; padding: 0 14px;
            }
            QLineEdit:focus { border: 1px solid #22d3ee; background-color: #0c1a30; }
            QLineEdit::placeholder { color: #2a4060; }
        """)
        self._input.setFixedHeight(44)
        self._input.returnPressed.connect(self._send_text)
        ilay.addWidget(self._input)

        send_btn = GlowButton("SEND ▸", "#22d3ee")
        send_btn.setFixedWidth(90)
        send_btn.clicked.connect(self._send_text)
        ilay.addWidget(send_btn)

        # Stop button — visible only while responding/speaking
        self._stop_btn = GlowButton("■ STOP", "#ef4444")
        self._stop_btn.setFixedWidth(90)
        self._stop_btn.clicked.connect(self._stop_response)
        self._stop_btn.setVisible(False)       # hidden by default
        ilay.addWidget(self._stop_btn)

        lay.addWidget(input_bar)
        return panel

    def _make_right_panel(self):
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet("""
            QFrame { background-color: #07101f; border-left: 1px solid #0f2040; }
        """)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 20, 14, 20)
        lay.setSpacing(12)

        sys_lbl = QLabel("SYSTEM STATUS")
        sys_lbl.setStyleSheet(
            "color: #1e4060; font-family: 'Courier New'; font-size: 8px; letter-spacing: 3px;")
        lay.addWidget(sys_lbl)

        self._card_state  = InfoCard("CORE STATE", "IDLE",     "#22d3ee")
        self._card_msgs   = InfoCard("MESSAGES",   "0",        "#a855f7")
        self._card_input  = InfoCard("INPUT MODE", "TEXT",     "#22c55e")
        self._card_model  = InfoCard("ENGINE",     "AURA-X",   "#f59e0b")
        self._card_uptime = InfoCard("UPTIME",     "00:00:00", "#64748b")

        for c in [self._card_state, self._card_msgs, self._card_input,
                  self._card_model, self._card_uptime]:
            lay.addWidget(c)

        lay.addWidget(self._divider())

        log_lbl = QLabel("ACTIVITY LOG")
        log_lbl.setStyleSheet(
            "color: #1e4060; font-family: 'Courier New'; font-size: 8px; letter-spacing: 3px;")
        lay.addWidget(log_lbl)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFrameShape(QFrame.Shape.NoFrame)
        self._log.setStyleSheet("""
            QTextEdit {
                background-color: transparent; color: #334155;
                font-family: 'Courier New'; font-size: 9px; border: none; padding: 0;
            }
        """)
        lay.addWidget(self._log, 1)
        lay.addStretch()
        return panel

    def _divider(self):
        d = QFrame(); d.setFixedHeight(1)
        d.setStyleSheet("background: #0f2040; margin: 4px 0;")
        return d

    # ─── STATE ─────────────────────────────────────────────

    def _set_state(self, state: str):
        self._status.set_state(state)
        self.orb.set_state(state)
        labels = {
            "idle":      ("● IDLE",       "#475569"),
            "listening": ("◉ LISTENING",  "#22c55e"),
            "thinking":  ("⟳ THINKING",   "#f59e0b"),
            "speaking":  ("◈ SPEAKING",   "#a855f7"),
            "responding":("▶ RESPONDING", "#22d3ee"),
            "error":     ("✕ ERROR",      "#ef4444"),
        }
        txt, col = labels.get(state, ("● IDLE", "#475569"))
        self._orb_label.setText(txt)
        self._orb_label.setStyleSheet(
            f"color: {col}; font-family: 'Courier New'; font-size: 9px; letter-spacing: 2px;")
        self._card_state.set_value(state.upper())
        self._voice_btn.set_active(state == "listening")
        self._card_input.set_value("VOICE" if state == "listening" else "TEXT")
        self._log_entry(state.upper())

        # Show stop button only while AI is actively responding/speaking
        is_active = state in ("speaking", "responding")
        self._stop_btn.setVisible(is_active)

    def _log_entry(self, text):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.append(
            f"<span style='color:#1e3a5f;'>{ts}</span> "
            f"<span style='color:#334155;'>{text}</span>")

    # ─── GREETING ──────────────────────────────────────────

    def _send_greeting(self):
        try:
            from services.greeting_service import generate_intro
            intro = generate_intro()
        except Exception:
            intro = "AURA-X neural interface online. How may I assist?"
        self._chat.append_system("System initialized. Secure connection established.")
        self._stream_response(intro)
        QTimer.singleShot(3000, self._handle_voice)

    # ─── TEXT SEND ─────────────────────────────────────────

    def _send_text(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._chat.append_user(text)
        self._msg_count += 1
        self._card_msgs.set_value(str(self._msg_count))
        self._set_state("thinking")

        self._ai_worker = AIWorker(text)
        self._ai_worker.finished.connect(self._handle_response)
        self._ai_worker.start()

    # ─── VOICE ─────────────────────────────────────────────

    def _handle_voice(self):
        if self.is_listening or self.is_speaking:
            return
        self.is_listening = True
        self._set_state("listening")
        self._voice_worker = VoiceWorker()
        self._voice_worker.finished.connect(self._on_voice_input)
        self._voice_worker.start()

    def _on_voice_input(self, command):
        self.is_listening = False
        if not command:
            self._set_state("idle")
            self._chat.append_system("No voice input detected.")
            return
        command = command.lower()
        self._chat.append_user(command)
        self._msg_count += 1
        self._card_msgs.set_value(str(self._msg_count))

        if any(x in command for x in ["shutdown aura", "exit aura", "close yourself", "quit aura"]):
            self._stream_response("Shutting down. Goodbye.")
            QTimer.singleShot(2500, self.close)
            return

        self._set_state("thinking")
        self._ai_worker = AIWorker(command)
        self._ai_worker.finished.connect(self._handle_response)
        self._ai_worker.start()

    # ─── RESPONSE ──────────────────────────────────────────

    def _handle_response(self, response: str):
        self.is_speaking = True
        self._stream_response(response)

    def _stream_response(self, response: str):
        """
        Core method — kicks off the StreamingResponseEngine which
        types and speaks each sentence simultaneously.
        """
        # Cancel any in-progress stream
        if self._stream_engine:
            self._stream_engine.stop()
            self._stream_engine = None

        self._set_state("speaking")

        self._stream_engine = StreamingResponseEngine(
            response=response,
            chat=self._chat,
            on_state_change=self._set_state,
            on_all_done=self._on_stream_done,
        )
        self._stream_engine.start()

    def _on_stream_done(self):
        """Called by StreamingResponseEngine when all sentences are done."""
        self.is_speaking = False
        self._stream_engine = None
        self._set_state("idle")
        # Resume listening after a short pause
        QTimer.singleShot(800, self._handle_voice)

    def _stop_response(self):
        """Immediately halt typing + TTS, append a stopped marker, go idle."""
        if self._stream_engine:
            self._stream_engine.stop()
            self._stream_engine = None
        self.is_speaking = False
        # Small visual marker so the user sees where it was cut
        self._chat.moveCursor(QTextCursor.MoveOperation.End)
        self._chat.insertHtml(
            "<span style='color:#475569;font-family:Courier New;"
            "font-size:10px;'> ◼ stopped</span><br/>"
        )
        self._set_state("idle")

    # ─── CLEAR CHAT ────────────────────────────────────────

    def _clear_chat(self):
        if self._stream_engine:
            self._stream_engine.stop()
            self._stream_engine = None
        self._chat.clear()
        self._msg_count = 0
        self._card_msgs.set_value("0")
        self._chat.append_system("Chat cleared.")

    # ─── CLOCK ─────────────────────────────────────────────

    def _start_clock(self):
        from datetime import datetime
        self._start_time = datetime.now()
        t = QTimer(self)
        t.timeout.connect(self._update_clock)
        t.start(1000)

    def _update_clock(self):
        from datetime import datetime
        now = datetime.now()
        self._clock_label.setText(now.strftime("%H:%M:%S"))
        elapsed = now - self._start_time
        h, rem = divmod(int(elapsed.total_seconds()), 3600)
        m, s = divmod(rem, 60)
        self._card_uptime.set_value(f"{h:02}:{m:02}:{s:02}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def run_app():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    from PyQt6.QtGui import QPalette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#060c1a"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#07101f"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#0a1628"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#0f2040"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#22d3ee"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#22d3ee"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000"))
    app.setPalette(palette)
    window = AuraApp()
    window.show()
    sys.exit(app.exec())

