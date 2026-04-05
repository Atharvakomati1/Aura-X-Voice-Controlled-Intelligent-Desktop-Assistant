import tkinter as tk
import threading
import time
from core.brain import process_command

# COLORS
BG = "#020617"
PANEL = "#0f172a"
ACCENT = "#22d3ee"
TEXT = "#e2e8f0"
USER = "#2563eb"
BOT = "#111827"

def run_app():
    app = AuraApp()
    app.run()

class AuraApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AURA-X AI")
        self.root.geometry("1100x720")
        self.root.configure(bg=BG)

        self.build_ui()
        self.animate_glow()
    
    def send_text(self):
        user_input = self.entry.get().strip()
        if not user_input:
            return

        self.add_message(user_input, "user")

        from core.brain import process_command
        response = process_command(user_input)

        self.add_message(response, "bot")

        self.entry.delete(0, tk.END)
    def send_text_event(self, event):
        self.send_text()
    def build_ui(self):
        # ===== TOP BAR =====
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill=tk.X)

        self.title = tk.Label(top, text="AURA-X SYSTEM", fg=ACCENT,
                              bg=BG, font=("Consolas", 18, "bold"))
        self.title.pack(pady=10)

        # ===== MAIN =====
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)

        # ===== LEFT PANEL =====
        left = tk.Frame(main, bg=PANEL, width=220)
        left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left, text="CONTROL", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 12, "bold")).pack(pady=15)

        self.voice_btn = tk.Button(left, text="🎤 VOICE", bg=ACCENT, fg="black")
        self.voice_btn.pack(pady=10, padx=10, fill=tk.X)

        tk.Button(left, text="⚙ SETTINGS", bg=PANEL, fg=TEXT).pack(pady=10, padx=10, fill=tk.X)
        tk.Button(left, text="📁 MEMORY", bg=PANEL, fg=TEXT).pack(pady=10, padx=10, fill=tk.X)

        # ===== CHAT AREA =====
        center = tk.Frame(main, bg=BG)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_box = tk.Text(center, bg=BG, fg=TEXT,
                                font=("Consolas", 11), bd=0)
        self.chat_box.pack(fill=tk.BOTH, expand=True, padx=10)

        # ===== INPUT =====
        bottom = tk.Frame(center, bg=BG)
        bottom.pack(fill=tk.X)

        self.entry = tk.Entry(bottom, bg=PANEL, fg=TEXT,
                              insertbackground="white",
                              font=("Consolas", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.entry.bind("<Return>", self.send_text_event)
        send = tk.Button(bottom, text="➤", bg=ACCENT,
                         command=self.send_text, width=5)
        send.pack(side=tk.RIGHT, padx=10)

        # ===== RIGHT PANEL =====
        right = tk.Frame(main, bg=PANEL, width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right, text="SYSTEM", fg=ACCENT, bg=PANEL,
                 font=("Consolas", 12, "bold")).pack(pady=15)

        self.status = tk.Label(right, text="Status: IDLE", fg=TEXT, bg=PANEL)
        self.status.pack(pady=10)

        self.cpu = tk.Label(right, text="CPU: --%", fg=TEXT, bg=PANEL)
        self.cpu.pack(pady=10)

    # ===== MESSAGE ADD =====
    def add_message(self, text, sender="user"):
        if sender == "user":
            self.chat_box.insert(tk.END, f"\nYOU: {text}\n", "user")
        else:
            self.chat_box.insert(tk.END, f"\nAURA-X: ", "bot")
            self.typing_effect(text)

        self.chat_box.see(tk.END)

    # ===== TYPING EFFECT =====
    def typing_effect(self, text):
        def run():
            self.status.config(text="Status: THINKING")
            for char in text:
                self.chat_box.insert(tk.END, char)
                self.chat_box.update()
                time.sleep(0.02)
            self.chat_box.insert(tk.END, "\n")
            self.status.config(text="Status: IDLE")

        threading.Thread(target=run).start()

    # ===== SEND =====
    def send_text(self):
        user_input = self.entry.get()
        if not user_input:
            return

        self.add_message(user_input, "user")

        # fake AI response for now
        response = process_command(user_input)
        self.add_message(response, "bot")

        self.entry.delete(0, tk.END)

    # ===== GLOW ANIMATION =====
    def animate_glow(self):
        def loop():
            colors = ["#22d3ee", "#06b6d4", "#0891b2"]
            i = 0
            while True:
                self.title.config(fg=colors[i % len(colors)])
                i += 1
                time.sleep(0.5)

        threading.Thread(target=loop, daemon=True).start()

    def run(self):
        self.root.mainloop()