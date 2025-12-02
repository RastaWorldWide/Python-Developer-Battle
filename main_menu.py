# main_menu.py
import tkinter as tk
from tkinter import messagebox
import sys
import os
import webbrowser

sys.path.append(os.path.dirname(__file__))

# Цвета (VS Code Dark+)
BG = "#1e1e1e"
FG = "white"
ACCENT = "#4ec9b0"
SECONDARY = "#6a9955"
WARNING = "#d7ba7d"
DANGER = "#f44747"
DARK_BG = "#2d2d2d"


class GameApp:
    """Главный класс приложения — управляет экранами"""
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Python Developer Battle")
        self.root.geometry("800x600")
        self.root.minsize(800, 650)
        self.root.configure(bg=BG)

        self.default_geometry = "800x600"
        self.is_fullscreen = False

        # Глобальные настройки — доступны всем экранам
        self.settings = {
            "sound": True,
            "pypi_check": True,
            "offline_mode": False
        }

        # Текущий экран
        self.current_screen = None

        self.bind_global_keys()
        self.show_main_menu()

    def bind_global_keys(self):
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.on_escape)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.root.geometry(self.default_geometry)
        # Обновим UI, если экран поддерживает
        if hasattr(self.current_screen, "update_fullscreen_state"):
            self.current_screen.update_fullscreen_state()

    def on_escape(self, event=None):
        """Esc → выход из полноэкранного режима, или возврат в главное меню"""
        if self.is_fullscreen:
            self.toggle_fullscreen()
        elif not isinstance(self.current_screen, MainMenuScreen):
            self.show_main_menu()

    # === Управление экранами ===
    def show_main_menu(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = MainMenuScreen(self.root, self)

    def show_settings(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = SettingsScreen(self.root, self)

    def show_about(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = AboutScreen(self.root, self)

    def start_local(self):
        self.root.withdraw()
        try:
            from local_game import LocalGameApp
            game_win = tk.Toplevel()
            game_win.title("🐍 Локальный режим")
            game_win.geometry("720x520")
            game_win.configure(bg=BG)
            game_win.protocol("WM_DELETE_WINDOW", lambda: self._on_game_close(game_win))
            # Передаём актуальные настройки
            LocalGameApp(game_win, self.settings)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Локальный режим недоступен:\n{e}")
            self.root.deiconify()

    def start_online(self):
        self.root.withdraw()
        try:
            from online_game import OnlineGameApp
            game_win = tk.Toplevel()
            game_win.title("🌍 Онлайн-режим")
            game_win.geometry("720x560")
            game_win.configure(bg=BG)
            game_win.protocol("WM_DELETE_WINDOW", lambda: self._on_game_close(game_win))
            OnlineGameApp(game_win, self.settings)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Онлайн-режим недоступен:\n{e}")
            self.root.deiconify()

    def _on_game_close(self, win):
        win.destroy()
        self.root.deiconify()
        self.show_main_menu()  # гарантируем возврат


# === Экран: Главное меню ===
class MainMenuScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        # Заголовок
        tk.Label(
            self.frame, text="🐍 PYTHON DEVELOPER BATTLE",
            font=("Consolas", 28, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(40, 10))

        tk.Label(
            self.frame, text="Соревнуйтесь в знании Python-библиотек!",
            font=("Consolas", 14), fg=WARNING, bg=BG
        ).pack(pady=(0, 30))

        # Правила
        rules = (
            "🎯 Правила:\n"
            "  • По очереди называйте реальные библиотеки Python\n"
            "  • На ход — 10 секунд ⏱\n"
            "  • Нельзя повторять или выдумывать\n"
            "  • Побеждает тот, кто устоит дольше!"
        )
        tk.Label(
            self.frame, text=rules,
            font=("Consolas", 11), fg=FG, bg=BG,
            justify="left", anchor="w", padx=50
        ).pack(pady=(0, 30), anchor="w")

        # Кнопки
        btn_frame = tk.Frame(self.frame, bg=BG)
        btn_frame.pack()

        cfg = {"font": ("Consolas", 13, "bold"), "width": 26, "height": 2, "relief": "flat"}

        tk.Button(btn_frame, text="🎮 Локально (1 vs 1)", bg=ACCENT, fg="black", command=app.start_local, **cfg).pack(pady=8)
        tk.Button(btn_frame, text="🌍 Онлайн (по коду)", bg=SECONDARY, fg="black", command=app.start_online, **cfg).pack(pady=8)
        tk.Button(btn_frame, text="⚙️ Настройки", bg=DARK_BG, fg=FG, command=app.show_settings, **cfg).pack(pady=8)
        tk.Button(btn_frame, text="ℹ️ О программе", bg=DARK_BG, fg=FG, command=app.show_about, **cfg).pack(pady=8)
        tk.Button(btn_frame, text="🚪 Выйти", bg=DANGER, fg="white", command=app.root.quit, **cfg).pack(pady=(20, 8))

        # Easter egg
        app.root.bind("<Button-3>", lambda e: self.easter_egg())

    def easter_egg(self):
        try:
            import this
            messagebox.showinfo("Zen of Python", this.s)
        except:
            pass

    def destroy(self):
        self.frame.destroy()


# === Экран: Настройки ===
class SettingsScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        # Заголовок
        tk.Label(
            self.frame, text="⚙️ Настройки",
            font=("Consolas", 24, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(40, 30))

        # Параметры
        settings_frame = tk.Frame(self.frame, bg=BG)
        settings_frame.pack()

        # Звук
        self.sound_var = tk.BooleanVar(value=app.settings["sound"])
        tk.Checkbutton(
            settings_frame, text="🔊 Включить звуки",
            variable=self.sound_var,
            font=("Consolas", 12), bg=BG, fg=FG,
            selectcolor="#3a3a3a", command=self.apply
        ).pack(anchor="w", padx=50, pady=6)

        # PyPI
        self.pypi_var = tk.BooleanVar(value=app.settings["pypi_check"])
        tk.Checkbutton(
            settings_frame, text="✅ Проверять библиотеки в PyPI",
            variable=self.pypi_var,
            font=("Consolas", 12), bg=BG, fg=FG,
            selectcolor="#3a3a3a", command=self.apply
        ).pack(anchor="w", padx=50, pady=6)

        # Оффлайн
        self.offline_var = tk.BooleanVar(value=app.settings["offline_mode"])
        tk.Checkbutton(
            settings_frame, text="✈️ Оффлайн-режим (без интернета)",
            variable=self.offline_var,
            font=("Consolas", 12), bg=BG, fg=WARNING,
            selectcolor="#3a3a3a", command=self.apply
        ).pack(anchor="w", padx=50, pady=6)

        # Полноэкранный режим — КНОПКА (не чекбокс!)
        self.fullscreen_btn = tk.Button(
            settings_frame,
            text=self._get_fullscreen_text(),
            font=("Consolas", 12),
            bg=DARK_BG,
            fg=FG,
            width=28,
            height=1,
            relief="flat",
            command=app.toggle_fullscreen
        )
        self.fullscreen_btn.pack(pady=(20, 6))

        tk.Label(
            settings_frame,
            text="Изменения сохраняются мгновенно.",
            font=("Consolas", 9), fg="#6a9955", bg=BG
        ).pack(pady=(15, 0))

        # Нижняя панель
        bottom = tk.Frame(self.frame, bg=BG)
        bottom.pack(side="bottom", pady=20)

        tk.Button(
            bottom, text="← Назад в меню",
            font=("Consolas", 11), bg=DARK_BG, fg=FG,
            command=app.show_main_menu, width=20
        ).pack()

    def _get_fullscreen_text(self):
        return "🖥️ Выйти из полного экрана" if self.app.is_fullscreen else "🖥️ Включить полный экран"

    def update_fullscreen_state(self):
        self.fullscreen_btn.config(text=self._get_fullscreen_text())

    def apply(self):
        self.app.settings.update({
            "sound": self.sound_var.get(),
            "pypi_check": self.pypi_var.get(),
            "offline_mode": self.offline_var.get()
        })

    def destroy(self):
        self.frame.destroy()


# === Экран: О программе ===
class AboutScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame, text="ℹ️ О программе",
            font=("Consolas", 24, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(40, 20))

        info = (
            "🐍 Python Developer Battle\n\n"
            "Версия: 0.6.0 (MVP)\n"
            "Автор: RastaWorldWide\n"
            "Лицензия: MIT\n\n"
            "Технологии:\n"
            "• Python 3.9+\n"
            "• Tkinter\n"
            "• PyPI API\n"
            "• WebSocket (онлайн)\n\n"
            "Домен: prosoft-people.online"
        )
        tk.Label(
            self.frame, text=info,
            font=("Consolas", 11), fg=FG, bg=BG,
            justify="left", padx=50
        ).pack(pady=20)

        # Ссылки
        links = [
            ("🌐 Сайт", "https://prosoft-people.online"),
            ("📦 PyPI", "https://pypi.org"),
            ("🐙 GitHub", "https://github.com/RastaWorldWide/Python-Developer-Battle")
        ]
        for text, url in links:
            lbl = tk.Label(
                self.frame, text=text,
                font=("Consolas", 11, "underline"),
                fg=SECONDARY, bg=BG, cursor="hand2"
            )
            lbl.pack(pady=4)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        # Назад
        tk.Button(
            self.frame, text="← Назад в меню",
            font=("Consolas", 11), bg=DARK_BG, fg=FG,
            command=app.show_main_menu, width=20
        ).pack(pady=(30, 0))

    def destroy(self):
        self.frame.destroy()


# === Запуск ===
if __name__ == "__main__":
    # Создаём заглушки, если нет файлов
    for name, code in {
        "local_game.py": '''import tkinter as tk\nclass LocalGameApp:\n    def __init__(self, root, settings):\n
                tk.Label(root, text="✅ Локальный режим запущен!\\n\\nНастройки: " + str(settings), 
                font=("Consolas", 12), fg="white", bg="#1e1e1e", justify="left").pack(expand=True)''',
        "online_game.py": '''import tkinter as tk\nclass OnlineGameApp:\n    def __init__(self, root, settings):\n
                tk.Label(root, text="🌍 Онлайн-режим", 
                font=("Consolas", 16), fg="white", bg="#1e1e1e").pack(expand=True)'''
    }.items():
        if not os.path.exists(name):
            with open(name, "w", encoding="utf-8") as f:
                f.write(code)

    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()