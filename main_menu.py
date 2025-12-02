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
ACCENT = "#4ec9b0"   # зелёный (start)
SECONDARY = "#6a9955"  # тёмно-зелёный
WARNING = "#d7ba7d"  # жёлтый
DANGER = "#f44747"   # красный (quit)
DARK_BG = "#2d2d2d"


class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Python Developer Battle")
        self.root.geometry("800x600")
        self.root.minsize(600, 450)
        self.root.configure(bg=BG)

        self.is_fullscreen = False
        self.default_geometry = "800x600"

        # Глобальные настройки
        self.settings = {
            "sound": True,
            "pypi_check": True,
            "offline_mode": False
        }

        self.bind_keys()
        self.show_main_menu()

    def bind_keys(self):
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.on_escape)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.root.geometry(self.default_geometry)
        if hasattr(self.current_screen, "update_ui"):
            self.current_screen.update_ui()

    def on_escape(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()
        elif not isinstance(self.current_screen, MainMenuScreen):
            self.show_main_menu()

    def show_main_menu(self):
        self._switch_screen(MainMenuScreen)

    def show_start_modes(self):
        self._switch_screen(StartModesScreen)

    def show_settings(self):
        self._switch_screen(SettingsScreen)

    def show_about(self):
        self._switch_screen(AboutScreen)

    def _switch_screen(self, ScreenClass):
        if hasattr(self, 'current_screen') and self.current_screen:
            self.current_screen.destroy()
        self.current_screen = ScreenClass(self.root, self)

    # === Запуск режимов (заглушки) ===
    def start_local(self):
        self._launch_game("local_game", "🐍 Локальный режим (1 на 1)", "720x520")

    def start_online(self):
        self._launch_game("online_game", "🌍 Онлайн-режим", "720x560")

    def start_vs_bot(self):
        messagebox.showinfo("🤖 Режим против бота", "Скоро будет доступен!")

    def _launch_game(self, module_name, title, geometry):
        self.root.withdraw()
        try:
            module = __import__(module_name)
            game_win = tk.Toplevel()
            game_win.title(title)
            game_win.geometry(geometry)
            game_win.configure(bg=BG)
            game_win.protocol("WM_DELETE_WINDOW", lambda: self._on_game_close(game_win))
            getattr(module, f"{module_name.replace('_', ' ').title().replace(' ', '')}App")(game_win, self.settings)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить:\n{e}")
            self.root.deiconify()

    def _on_game_close(self, win):
        win.destroy()
        self.root.deiconify()
        self.show_main_menu()


# === Экран 1: Главное меню (4 кнопки) ===
class MainMenuScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        # Заголовок
        tk.Label(
            self.frame, text="🐍 PYTHON DEVELOPER BATTLE",
            font=("Consolas", 26, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(50, 60))

        # 4 кнопки по центру
        btn_cfg = {"font": ("Consolas", 14, "bold"), "width": 20, "height": 2, "relief": "flat"}

        tk.Button(self.frame, text="▶️ Start",      bg=ACCENT,   fg="black", command=app.show_start_modes, **btn_cfg).pack(pady=10)
        tk.Button(self.frame, text="⚙️ Settings",  bg=DARK_BG,  fg=FG,      command=app.show_settings,   **btn_cfg).pack(pady=10)
        tk.Button(self.frame, text="ℹ️ About",     bg=DARK_BG,  fg=FG,      command=app.show_about,      **btn_cfg).pack(pady=10)
        tk.Button(self.frame, text="⏹️ Quit",      bg=DANGER,   fg="white", command=app.root.quit,       **btn_cfg).pack(pady=10)

        # Подсказка
        tk.Label(
            self.frame, text="Нажмите F11 для полноэкранного режима",
            font=("Consolas", 9), fg="#6a9955", bg=BG
        ).pack(side="bottom", pady=20)

    def destroy(self):
        self.frame.destroy()


# === Экран 2: Start → выбор режима ===
class StartModesScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame, text="▶️ Выберите режим игры",
            font=("Consolas", 22, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(50, 40))

        btn_cfg = {"font": ("Consolas", 13, "bold"), "width": 26, "height": 2, "relief": "flat"}

        tk.Button(self.frame, text="🎮 1 на 1 (локально)", bg=ACCENT,   fg="black", command=app.start_local,  **btn_cfg).pack(pady=12)
        tk.Button(self.frame, text="🌍 Онлайн (по коду)",  bg=SECONDARY, fg="black", command=app.start_online, **btn_cfg).pack(pady=12)
        tk.Button(self.frame, text="🤖 Против бота",       bg="#5a5a5a", fg="#ccc",  command=app.start_vs_bot, state="normal", **btn_cfg).pack(pady=12)

        # Кнопка назад
        tk.Button(
            self.frame, text="← Назад", font=("Consolas", 11),
            bg="#3a3a3a", fg=FG, width=12, command=app.show_main_menu
        ).pack(pady=(40, 0))

    def destroy(self):
        self.frame.destroy()


# === Экран 3: Settings ===
class SettingsScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame, text="⚙️ Настройки",
            font=("Consolas", 24, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(50, 30))

        # Переключатели
        self.sound_var = tk.BooleanVar(value=app.settings["sound"])
        self.pypi_var = tk.BooleanVar(value=app.settings["pypi_check"])
        self.offline_var = tk.BooleanVar(value=app.settings["offline_mode"])

        check_cfg = {"font": ("Consolas", 12), "bg": BG, "fg": FG, "selectcolor": "#3a3a3a"}

        tk.Checkbutton(self.frame, text="🔊 Звуки", variable=self.sound_var, command=self.apply, **check_cfg).pack(pady=6)

        # Кнопка полного экрана
        self.fs_btn = tk.Button(
            self.frame, text=self._fs_text(), font=("Consolas", 12),
            bg=DARK_BG, fg=FG, width=28, height=1, relief="flat",
            command=app.toggle_fullscreen
        )
        self.fs_btn.pack(pady=(25, 10))

        tk.Button(self.frame, text="← Назад", font=("Consolas", 11), bg="#3a3a3a", fg=FG, width=12, command=app.show_main_menu).pack(pady=(30, 0))

    def _fs_text(self):
        return "🖥️ Выйти из полного экрана" if self.app.is_fullscreen else "🖥️ Полный экран"

    def update_ui(self):
        self.fs_btn.config(text="Полный экран")

    def apply(self):
        self.app.settings.update({
            "sound": self.sound_var.get(),
            "pypi_check": self.pypi_var.get(),
            "offline_mode": self.offline_var.get()
        })

    def destroy(self):
        self.frame.destroy()


# === Экран 4: About (правила + info) ===
class AboutScreen:
    def __init__(self, parent, app: GameApp):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(expand=True, fill="both")

        tk.Label(
            self.frame, text="ℹ️ О программе",
            font=("Consolas", 24, "bold"), fg=ACCENT, bg=BG
        ).pack(pady=(40, 20))

        # Правила
        rules = (
            "🎯 Правила игры:\n"
            "• Два игрока по очереди называют реальные библиотеки Python.\n"
            "• На каждый ход даётся 10 секунд.\n"
            "• Нельзя повторять или называть несуществующие пакеты.\n"
            "• Побеждает тот, кто сделал больше ходов (или у кого осталось время)."
        )
        tk.Label(
            self.frame, text=rules,
            font=("Consolas", 11), fg=FG, bg=BG,
            justify="left", padx=40, wraplength=700
        ).pack(pady=(0, 30))

        # Информация
        info = (
            "🐍 Python Developer Battle — игра для Python-разработчиков.\n"
            "Версия: 0.7.0 (MVP)\n"
            "Автор: RastaWorldWide\n"
            "GitHub: github.com/RastaWorldWide/Python-Developer-Battle\n"
            "Домен: prosoft-people.online"
        )
        tk.Label(
            self.frame, text=info,
            font=("Consolas", 10), fg="#d7ba7d", bg=BG,
            justify="center"
        ).pack(pady=10)

        tk.Button(self.frame, text="← Назад", font=("Consolas", 11), bg="#3a3a3a", fg=FG, width=12, command=app.show_main_menu).pack(pady=(30, 0))

    def destroy(self):
        self.frame.destroy()


# === Запуск ===
if __name__ == "__main__":
    # Создаём минимальные заглушки, если файлов нет
    for name in ["local_game.py", "online_game.py"]:
        if not os.path.exists(name):
            with open(name, "w", encoding="utf-8") as f:
                f.write(f'''
import tkinter as tk
class {name.replace(".py", "").title().replace("_", "")}App:
    def __init__(self, root, settings):
        tk.Label(root, text="{name[:-3].upper()} MODE\\n\\nНастройки: " + str(settings),
                 font=("Consolas", 14), fg="white", bg="#1e1e1e", justify="center").pack(expand=True, pady=50)
                ''')

    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()