import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import os

# === Настройки ===
TIME_LIMIT = 10  # секунд на ход
USE_SOUND = True  # переключи в False, если не хочешь звуков

# === Кэш и флаги ===
_pypi_cache = {}
_pypi_offline_mode = False


# === Вспомогательные функции ===
def is_valid_lib_name(name: str) -> bool:
    if not name or not name.replace('-', '').replace('_', '').isalnum():
        return False
    if not (name[0].isalpha() or name[0] == '_'):
        return False
    forbidden = {'import', 'from', 'def', 'class', 'pass', 'True', 'False', 'None', ''}
    return name.lower() not in forbidden


def is_real_pypi_package(name: str, timeout: float = 3.0) -> bool:
    if _pypi_offline_mode:
        return True
    name = name.lower()
    if name in _pypi_cache:
        return _pypi_cache[name]
    try:
        url = f"https://pypi.org/pypi/{name}/json"
        response = requests.get(url, timeout=timeout)
        exists = response.status_code == 200
        _pypi_cache[name] = exists
        return exists
    except Exception:
        return True  # мягкий фолбэк


# === Звуки (опционально) ===
def play_sound(sound_type="beep"):
    if not USE_SOUND:
        return
    try:
        if os.name == 'nt':  # Windows
            import winsound
            if sound_type == "success":
                winsound.Beep(800, 200)
            elif sound_type == "timeout":
                winsound.Beep(300, 500)
            else:
                winsound.Beep(600, 100)
        else:
            # Кроссплатформенно: системный звук
            print("\a", end="", flush=True)
    except Exception:
        pass


# === Основной класс игры ===
class PythonDevBattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Python Developer Battle")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        # Состояние игры
        self.players = ["Игрок 1", "Игрок 2"]
        self.current_turn = 0
        self.used_libs = set()
        self.scores = [0, 0]
        self.timer_running = False
        self.time_left = TIME_LIMIT
        self.input_thread = None

        self.setup_ui()
        self.update_turn_display()
        self.start_timer()

    def setup_ui(self):
        # Заголовок
        self.title_label = tk.Label(
            self.root, text="Python Developer Battle",
            font=("Consolas", 20, "bold"), fg="#4ec9b0", bg="#1e1e1e"
        )
        self.title_label.pack(pady=(20, 10))

        # Информация о ходе и счёте
        self.info_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.info_frame.pack(pady=5)

        self.turn_label = tk.Label(
            self.info_frame, text="", font=("Consolas", 14), fg="white", bg="#1e1e1e"
        )
        self.turn_label.pack()

        self.score_label = tk.Label(
            self.info_frame, text="", font=("Consolas", 12), fg="#d7ba7d", bg="#1e1e1e"
        )
        self.score_label.pack()

        # Таймер (анимированный)
        self.timer_canvas = tk.Canvas(self.root, width=200, height=30, bg="#2d2d2d", highlightthickness=0)
        self.timer_canvas.pack(pady=10)
        self.timer_text = self.timer_canvas.create_text(100, 15, text="10", fill="white", font=("Consolas", 16))

        # Поле ввода
        self.input_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.input_frame.pack(pady=10)

        self.entry = tk.Entry(
            self.input_frame, font=("Consolas", 14), width=30, justify="center",
            bg="#2d2d2d", fg="white", insertbackground="white"
        )
        self.entry.pack(side=tk.LEFT, padx=(0, 10))
        self.entry.bind("<Return>", self.on_submit)

        self.submit_btn = tk.Button(
            self.input_frame, text="Отправить", font=("Consolas", 12),
            command=self.on_submit, bg="#4ec9b0", fg="black", relief="flat"
        )
        self.submit_btn.pack(side=tk.LEFT)

        # Список названных библиотек
        self.lib_label = tk.Label(
            self.root, text="Названо:", font=("Consolas", 12, "underline"),
            fg="#c586c0", bg="#1e1e1e"
        )
        self.lib_label.pack(pady=(20, 5))

        self.lib_listbox = tk.Listbox(
            self.root, height=8, width=60, font=("Consolas", 10),
            bg="#2d2d2d", fg="white", selectbackground="#3e3e3e"
        )
        self.lib_listbox.pack(pady=5)

        # Подсказка
        self.hint_label = tk.Label(
            self.root,
            text="Введите имя библиотеки (как в pip install) и нажмите Enter или кнопку",
            font=("Consolas", 9), fg="#6a9955", bg="#1e1e1e", wraplength=600
        )
        self.hint_label.pack(pady=(10, 0))

    def update_turn_display(self):
        current_player = self.players[self.current_turn]
        self.turn_label.config(text=f"→ Ход: {current_player}")
        self.score_label.config(text=f"Счёт: {self.players[0]} — {self.scores[0]} | {self.players[1]} — {self.scores[1]}")
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def start_timer(self):
        self.time_left = TIME_LIMIT
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
        # Цвет: зелёный → жёлтый → красный
        if self.time_left > 5:
            color = "#4ec9b0"   # зелёный
        elif self.time_left > 2:
            color = "#d7ba7d"   # жёлтый
        else:
            color = "#f44747"   # красный

        self.timer_canvas.itemconfig(self.timer_text, text=str(self.time_left), fill=color)
        # Анимация "пульсации" при <3 сек
        if self.time_left <= 2:
            self.timer_canvas.config(bg="#3e2a2a" if self.time_left % 2 else "#2d2d2d")

    def on_timeout(self):
        if not self.timer_running:
            return
        self.timer_running = False
        play_sound("timeout")
        current_player = self.players[self.current_turn]
        messagebox.showerror("⏰ Тайм-аут!", f"{current_player} не успел(а)!")
        self.end_game()

    def on_submit(self, event=None):
        if not self.timer_running:
            return

        lib = self.entry.get().strip()
        if not lib:
            return

        self.timer_running = False  # останавливаем таймер
        threading.Thread(target=self.process_submission, args=(lib,), daemon=True).start()

    def process_submission(self, lib):
        # Выполняем проверки в фоне, чтобы не фризить UI
        lib_clean = lib.lower()

        error = None
        if not is_valid_lib_name(lib_clean):
            error = f"'{lib}' — некорректное имя библиотеки."
        elif lib_clean in self.used_libs:
            error = f"'{lib}' уже называли!"
        elif not is_real_pypi_package(lib_clean):
            error = f"'{lib}' не существует в PyPI!"

        # Обновляем UI в основном потоке
        def update_ui():
            if error:
                play_sound()
                messagebox.showerror("❌ Ошибка", error)
                self.end_game()
            else:
                play_sound("success")
                self.used_libs.add(lib_clean)
                self.scores[self.current_turn] += 1
                self.lib_listbox.insert(tk.END, f"{len(self.used_libs):2}. {lib_clean}")
                self.lib_listbox.see(tk.END)

                # Передаём ход
                self.current_turn = 1 - self.current_turn
                self.update_turn_display()
                self.start_timer()

        self.root.after(0, update_ui)

    def end_game(self):
        self.timer_running = False
        p1, p2 = self.scores
        result = ""
        if p1 > p2:
            result = f"🏆 Победил(а) {self.players[0]}!"
        elif p2 > p1:
            result = f"🏆 Победил(а) {self.players[1]}!"
        else:
            result = "🤝 Ничья!"

        summary = (
            f"Итог: {self.players[0]} — {p1}, {self.players[1]} — {p2}\n\n"
            f"Всего библиотек: {len(self.used_libs)}\n"
            f"{result}"
        )
        messagebox.showinfo("Игра окончена", summary)
        self.root.quit()


# === Запуск ===
if __name__ == "__main__":
    root = tk.Tk()
    app = PythonDevBattleApp(root)
    root.mainloop()
