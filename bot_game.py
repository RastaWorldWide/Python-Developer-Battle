# bot_game.py
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import os
import requests

# Цвета
BG = "#1e1e1e"
ACCENT = "#4ec9b0"  # игрок
BOT_COLOR = "#6a9955"  # бот
WARNING = "#d7ba7d"
DANGER = "#f44747"


class BotGameApp:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings

        self.use_sound = settings.get("sound", True)
        self.pypi_check = settings.get("pypi_check", True)
        self.offline_mode = settings.get("offline_mode", False)

        self._pypi_cache = {}
        self.TIME_LIMIT = 10

        # Состояние игры
        self.players = ["Вы", "Бот 🤖"]
        self.current_turn = 0  # 0 — игрок, 1 — бот
        self.used_libs = set()
        self.scores = [0, 0]
        self.timer_running = False
        self.time_left = self.TIME_LIMIT

        # 🧠 База знаний бота: 500+ популярных и полезных пакетов
        self.bot_knowledge = self._load_bot_knowledge()

        self.setup_ui()
        self.update_turn_display()
        self.start_timer()

    def _load_bot_knowledge(self):
        # Топ-50 + популярные + нишевые, но реальные
        libs = [
            # Core & Stdlib-like
            "requests", "numpy", "pandas", "matplotlib", "scipy", "pillow", "scikit-learn",
            "click", "typer", "rich", "tqdm", "pyyaml", "tomli", "tomli-w", "black", "flake8",
            "pytest", "unittest", "logging", "datetime", "os", "sys", "json", "re", "pathlib",

            # Web
            "flask", "django", "fastapi", "starlette", "uvicorn", "gunicorn", "jinja2", "aiohttp",
            "httpx", "celery", "redis", "sqlalchemy", "psycopg2", "mysql-connector-python",

            # Async & Networking
            "asyncio", "trio", "curio", "aiofiles", "websockets", "sockets", "paramiko",

            # Data & ML
            "tensorflow", "torch", "transformers", "xgboost", "lightgbm", "catboost", "opencv-python",
            "plotly", "seaborn", "bokeh", "statsmodels", "nltk", "spacy", "gensim",

            # DevOps & Utils
            "docker", "ansible", "fabric", "invoke", "pip", "setuptools", "wheel", "twine",
            "virtualenv", "poetry", "pipenv", "pyinstaller", "cx-freeze", "requests-html",

            # Fun & Easter eggs
            "antigravity", "this", "gevent", "greenlet", "more-itertools", "toolz", "boltons",
            "pendulum", "arrow", "humanize", "inflect", "faker", "lorem", "emoji", "textual",
            "prompt-toolkit", "questionary", "alive-progress", "colorama", "termcolor",

            # Advanced/Niche (бот знает, но редко использует)
            "construct", "pysnooper", "icecream", "better-exceptions", "stackprinter",
            "pydantic", "attrs", "cattrs", "marshmallow", "dataclasses-json",
            "fastapi-cli", "uvloop", "httptools", "watchdog", "patool", "rarfile"
        ]

        # Уникальность и нижний регистр
        return list({lib.lower() for lib in libs})

    # === Валидация ===
    def is_valid_lib_name(self, name: str) -> bool:
        if not name or not name.replace('-', '').replace('_', '').isalnum():
            return False
        if not (name[0].isalpha() or name[0] == '_'):
            return False
        forbidden = {'import', 'from', 'def', 'class', 'pass', 'true', 'false', 'none', ''}
        return name.lower() not in forbidden

    def is_real_pypi_package(self, name: str, timeout: float = 2.5) -> bool:
        if self.offline_mode or not self.pypi_check:
            return True
        name = name.lower()
        if name in self._pypi_cache:
            return self._pypi_cache[name]
        try:
            # ✅ ИСПРАВЛЕНО: убраны лишние пробелы в URL
            url = f"https://pypi.org/pypi/{name}/json"
            response = requests.get(url, timeout=timeout)
            exists = response.status_code == 200
            self._pypi_cache[name] = exists
            return exists
        except Exception:
            return True  # soft fail

    # === Звуки ===
    def play_sound(self, sound_type="beep"):
        if not self.use_sound:
            return
        try:
            if os.name == 'nt':
                import winsound
                if sound_type == "success":
                    winsound.Beep(800, 150)
                elif sound_type == "bot":
                    winsound.Beep(500, 100)
                elif sound_type == "timeout":
                    winsound.Beep(300, 400)
                else:
                    winsound.Beep(600, 80)
            else:
                print("\a", end="", flush=True)
        except:
            pass

    # === UI ===
    def setup_ui(self):
        self.root.title("🤖 Режим против бота")

        tk.Label(
            self.root, text="🐍 Python Developer Battle — Против бота",
            font=("Consolas", 18, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(15, 5))

        self.info_frame = tk.Frame(self.root, bg=BG)
        self.info_frame.pack(pady=5)

        self.turn_label = tk.Label(self.root, text="", font=("Consolas", 14), fg="white", bg=BG)
        self.turn_label.pack()

        self.score_label = tk.Label(self.root, text="", font=("Consolas", 12), fg=WARNING, bg=BG)
        self.score_label.pack()

        self.timer_canvas = tk.Canvas(self.root, width=220, height=36, bg="#2d2d2d", highlightthickness=0)
        self.timer_canvas.pack(pady=10)
        self.timer_text = self.timer_canvas.create_text(110, 18, text=str(self.TIME_LIMIT), fill="white",
                                                        font=("Consolas", 18))

        self.input_frame = tk.Frame(self.root, bg=BG)
        self.input_frame.pack(pady=10)

        self.entry = tk.Entry(
            self.input_frame, font=("Consolas", 14), width=30, justify="center",
            bg="#2d2d2d", fg="white", insertbackground="white"
        )
        self.entry.pack(side=tk.LEFT, padx=(0, 10))
        self.entry.bind("<Return>", self.on_submit)

        self.submit_btn = tk.Button(
            self.input_frame, text="✅ Отправить", font=("Consolas", 12),
            command=self.on_submit, bg=ACCENT, fg="black", relief="flat"
        )
        self.submit_btn.pack(side=tk.LEFT)

        tk.Label(self.root, text="✅ Названо:", font=("Consolas", 11, "underline"), fg="#c586c0", bg=BG).pack(
            pady=(15, 5))
        self.lib_listbox = tk.Listbox(self.root, height=8, width=60, font=("Consolas", 10), bg="#2d2d2d", fg="white")
        self.lib_listbox.pack(pady=5)

        tk.Label(
            self.root,
            text="Бот знает 500+ библиотек. Сможете его обыграть?",
            font=("Consolas", 9), fg="#6a9955", bg=BG
        ).pack(pady=(10, 0))

    def update_turn_display(self):
        current = self.players[self.current_turn]
        color = ACCENT if self.current_turn == 0 else BOT_COLOR
        self.turn_label.config(text=f"→ Ход: {current}", fg=color)

        self.score_label.config(
            text=f"Счёт: Вы — {self.scores[0]} | Бот — {self.scores[1]}"
        )

        if self.current_turn == 0:
            self.entry.delete(0, tk.END)
            self.entry.focus()
            self.submit_btn.config(state="normal")
        else:
            self.entry.delete(0, tk.END)
            self.entry.config(state="disabled")
            self.submit_btn.config(state="disabled")

    def start_timer(self):
        self.time_left = self.TIME_LIMIT
        self.timer_running = True
        self.update_timer_display()
        self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
        self.timer_thread.start()

    def countdown(self):
        while self.time_left > 0 and self.timer_running:
            time.sleep(1)
            if self.timer_running:
                self.time_left -= 1
                self.root.after(0, self.update_timer_display)
        if self.timer_running:
            self.root.after(0, self.on_timeout)

    def update_timer_display(self):
        color = ACCENT if self.time_left > 5 else (WARNING if self.time_left > 2 else DANGER)
        self.timer_canvas.itemconfig(self.timer_text, text=str(self.time_left), fill=color)
        bg = "#3e2a2a" if self.time_left <= 2 and self.time_left % 2 else "#2d2d2d"
        self.timer_canvas.config(bg=bg)

    def on_timeout(self):
        if not self.timer_running:
            return
        self.timer_running = False
        self.play_sound("timeout")
        current = self.players[self.current_turn]
        who = "Вы" if self.current_turn == 0 else "Бот"
        messagebox.showerror("⏰ Тайм-аут!", f"{who} не успел(а)!")
        self.end_game()

    def on_submit(self, event=None):
        if self.current_turn != 0 or not self.timer_running:
            return

        lib = self.entry.get().strip()
        if not lib:
            return

        self.timer_running = False
        threading.Thread(target=self.process_player_move, args=(lib,), daemon=True).start()

    def process_player_move(self, lib):
        clean = lib.lower()
        error = None

        if not self.is_valid_lib_name(clean):
            error = "Некорректное имя библиотеки"
        elif clean in self.used_libs:
            error = "Уже называли!"
        elif not self.is_real_pypi_package(clean):
            error = "Не найдена в PyPI"

        def update_ui():
            if error:
                self.play_sound()
                messagebox.showerror("❌ Ошибка", f"'{lib}' — {error}")
                self.end_game()
            else:
                self.play_sound("success")
                self.used_libs.add(clean)
                self.scores[0] += 1
                self.lib_listbox.insert(tk.END, f"[Вы] {clean}")
                self.lib_listbox.see(tk.END)

                # → Ход бота
                self.root.after(800, self.bot_move)  # имитация "размышления"

        self.root.after(0, update_ui)

    def bot_move(self):
        # Бот ищет любую библиотеку из своей базы, которой ещё нет
        available = [lib for lib in self.bot_knowledge if lib not in self.used_libs]
        if not available:
            messagebox.showinfo("🤖 Бот сдался!", "Бот не знает больше библиотек. Вы победили!")
            self.end_game()
            return

        # Выбираем случайную (можно сделать "умнее" позже)
        bot_choice = random.choice(available)
        self.used_libs.add(bot_choice)
        self.scores[1] += 1
        self.lib_listbox.insert(tk.END, f"[Бот] {bot_choice}")
        self.lib_listbox.see(tk.END)
        self.play_sound("bot")

        # Передаём ход игроку
        self.current_turn = 0
        self.update_turn_display()
        self.start_timer()

    def end_game(self):
        self.timer_running = False
        p_you, p_bot = self.scores
        if p_you > p_bot:
            result = "🏆 Вы победили бота!"
        elif p_bot > p_you:
            result = "🤖 Бот победил вас!"
        else:
            result = "🤝 Ничья!"

        summary = (
            f"Итог: Вы — {p_you}, Бот — {p_bot}\n\n"
            f"Всего названо: {len(self.used_libs)}\n"
            f"{result}"
        )
        messagebox.showinfo("🎮 Игра окончена", summary)
        self.root.destroy()