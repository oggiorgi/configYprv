import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import tarfile
import argparse
import stat

class ShellEmulator:
    def __init__(self, master, user, virtual_fs_path):
        self.master = master
        self.master.title("Shell Emulator")
        self.username = user
        self.virtual_fs_path = virtual_fs_path
        self.current_path = "/"
        self.history = []

        # GUI Components
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.label = tk.Label(master, text=f"{self.username}@shell>")
        self.label.pack(padx=10, pady=5)

        self.entry = tk.Entry(master)
        self.entry.pack(padx=10, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.execute_command)

        self.extract_virtual_fs()

    def extract_virtual_fs(self):
        if not os.path.exists(self.virtual_fs_path):
            messagebox.showerror("Ошибка", "Файл виртуальной файловой системы не найден.")
            return

        with tarfile.open(self.virtual_fs_path) as tar:
            tar.extractall(path="virtual_fs", filter=tarfile.data_filter)

    def execute_command(self, event):
        command = self.entry.get().strip()
        self.history.append(command)

        cmd_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:].strip()),
            "exit": self.master.quit,
            "touch": lambda: self.touch_file(command[6:].strip()),
            "chmod": lambda: self.change_permissions(command[6:].strip())
        }

        if command.split()[0] in cmd_dict:
            cmd_dict[command.split()[0]]()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

        self.entry.delete(0, tk.END)

    def list_files(self):
        try:
            files = os.listdir(f"virtual_fs{self.current_path}")
            output = "\n".join(files) if files else "Пустая директория\n"
            self.text_area.insert(tk.END, f"{output}\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def change_directory(self, path):
        if path == "..":
            if self.current_path != "/":
                parts = self.current_path.split("/")
                self.current_path = "/".join(parts[:-1]) or "/"
        else:
            new_path = os.path.join(f"virtual_fs{self.current_path}", path)
            if os.path.isdir(new_path):
                self.current_path = os.path.join(self.current_path, path).replace("//", "/")
            else:
                self.text_area.insert(tk.END, "Директория не найдена\n")

    def touch_file(self, filename):
        try:
            file_path = os.path.join(f"virtual_fs{self.current_path}", filename)
            with open(file_path, 'a'):
                pass
            self.text_area.insert(tk.END, f"Файл '{filename}' создан.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Ошибка при создании файла: {e}\n")

    def change_permissions(self, args):
        try:
            mode, filename = args.split()
            mode = int(mode, 8)
            file_path = os.path.join(f"virtual_fs{self.current_path}", filename)
            os.chmod(file_path, mode)
            self.text_area.insert(tk.END, f"Права файла '{filename}' изменены на {mode:o}.\n")
        except (ValueError, FileNotFoundError):
            self.text_area.insert(tk.END, "Ошибка: неверный формат команды или файл не найден.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор shell")
    parser.add_argument("--user", required=True, help="Имя пользователя")
    parser.add_argument("--fs", required=True, help="Путь к tar-архиву файловой системы")
    parser.add_argument("--script", help="Путь к стартовому скрипту")

    args = parser.parse_args()

    root = tk.Tk()
    app = ShellEmulator(root, args.user, args.fs)

    if args.script:
        try:
            with open(args.script, 'r') as script_file:
                for line in script_file:
                    app.execute_command(event=None)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл скрипта не найден.")

    root.mainloop()

