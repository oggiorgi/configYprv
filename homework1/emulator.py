import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import tarfile
import argparse


class ShellEmulator:
    def __init__(self, master, username, virtual_fs_path):
        self.master = master
        self.master.title("Shell Emulator")
        self.current_path = "/"
        self.history = []

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.username = username
        self.virtual_fs_path = virtual_fs_path

        self.label = tk.Label(master, text=f"{self.username}:{self.current_path}")
        self.label.pack(padx=10, pady=5)

        self.entry = tk.Entry(master)
        self.entry.pack(padx=10, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.execute_command)

        self.extract_virtual_fs()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description="Эмулятор командной строки.")
        parser.add_argument("--user", type=str, help="Имя пользователя.", required=False)
        parser.add_argument("--fs", type=str, help="Путь к архиву виртуальной файловой системы.", required=True)
        parser.add_argument("--script", type=str, help="Путь к скрипту с командами.", required=False)

        args = parser.parse_args()

        if not os.path.exists(args.fs):
            parser.error(f"Файл виртуальной файловой системы '{args.fs}' не найден.")

        return args

    def extract_virtual_fs(self):
        if not os.path.exists(self.virtual_fs_path):
            messagebox.showerror("Ошибка", "Файл виртуальной файловой системы не найден.")
            return

        with tarfile.open(self.virtual_fs_path) as tar:
            tar.extractall(path="virtual_fs", filter=tarfile.data_filter)

    def load_script(self, script_file):
        try:
            with open(script_file, 'r') as file:
                for line in file:
                    command = line.strip()
                    if command:
                        self.execute_command_from_script(command)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл скрипта {script_file} не найден.")

    def execute_command(self, event):
        command = self.entry.get()

        command_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:]),
            "pwd": self.print_working_directory,
            "exit": self.master.quit,
            "touch": lambda: self.touch_file(command[6:]),
            "chmod": lambda: self.chmod_file(command[6:]),
        }

        cmd_func = command_dict.get(command.split()[0], None)

        if cmd_func:
            cmd_func()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

        self.entry.delete(0, tk.END)

    def execute_command_from_script(self, command):
        command_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:]),
            "pwd": self.print_working_directory,
            "exit": self.master.quit,
            "touch": lambda: self.touch_file(command[6:]),
            "chmod": lambda: self.chmod_file(command[6:]),
        }

        cmd_func = command_dict.get(command.split()[0], None)

        if cmd_func:
            cmd_func()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

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
                parts.pop()
                self.current_path = "/".join(parts) or "/"
                self.label.config(text=f"{self.username}:{self.current_path}")
                return

        new_path = os.path.join(f"virtual_fs{self.current_path}", path)

        if os.path.isdir(new_path):
            self.current_path = new_path.replace("virtual_fs", "")
            self.label.config(text=f"{self.username}:{self.current_path}")
            return
        else:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def print_working_directory(self):
        current_dir = f"{self.username}:{self.current_path}\n"
        self.text_area.insert(tk.END, current_dir)

    def touch_file(self, filename):
        try:
            file_path = os.path.join(f"virtual_fs{self.current_path}", filename.strip())
            with open(file_path, 'a'):
                pass
            self.text_area.insert(tk.END, f"Файл '{filename}' создан.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Ошибка при создании файла '{filename}': {str(e)}\n")

    def chmod_file(self, command):
        try:
            parts = command.split()
            if len(parts) != 2:
                self.text_area.insert(tk.END, "Использование: chmod <права> <файл>\n")
                return

            permissions, filename = parts
            file_path = os.path.join(f"virtual_fs{self.current_path}", filename.strip())

            os.chmod(file_path, int(permissions, 8))
            self.text_area.insert(tk.END, f"Права для файла {filename} изменены на {permissions}\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Файл не найден\n")
        except PermissionError:
            self.text_area.insert(tk.END, "Нет доступа для изменения прав файла\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Ошибка при изменении прав: {str(e)}\n")


if __name__ == "__main__":
    args = ShellEmulator.parse_arguments()
    username = args.user or os.getlogin()

    root = tk.Tk()
    app = ShellEmulator(root, username, args.fs)

    if args.script:
        app.load_script(args.script)

    root.mainloop()
