import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from io import StringIO
import tkinter as tk
from emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):

    # Тестирование команды "ls"
    @patch('tarfile.open')
    @patch('tkinter.messagebox.showerror')
    @patch('os.listdir')
    def test_list_files(self, mock_listdir, mock_showerror, mock_tarfile):
        # Замокаем tarfile.open, чтобы избежать реального открытия архива
        mock_tarfile.return_value.__enter__.return_value.extractall = MagicMock()

        # Мокаем список файлов, чтобы вернуть фальшивые данные
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        root = tk.Tk()
        emulator = ShellEmulator(root, 'virtual_fs.tar')

        # Перехватываем вывод в текстовом поле
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            emulator.list_files()
            output = mock_stdout.getvalue().strip()

        # Проверяем, что в выводе присутствуют имена файлов
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)
        mock_showerror.assert_not_called()

    # Тестирование команды "cd" (смена директории)
    @patch('os.path.isdir')
    @patch('tkinter.messagebox.showerror')
    def test_change_directory(self, mock_showerror, mock_isdir):
        # Мокаем os.path.isdir, чтобы вернуть True для существующих директорий
        mock_isdir.return_value = True
        root = tk.Tk()
        emulator = ShellEmulator(root, 'virtual_fs.tar')

        # Пробуем сменить директорию на существующую
        emulator.change_directory("dir1")
        self.assertEqual(emulator.current_path, "/dir1")

        # Мокаем ошибку: директория не существует
        mock_isdir.return_value = False
        emulator.change_directory("dir_invalid")

        # Перехватываем вывод в текстовом поле
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            output = mock_stdout.getvalue().strip()

        # Проверяем, что вывод содержит ошибку
        self.assertIn("Директория не найдена", output)

    # Тестирование команды "cat" (вывод содержимого файла)
    @patch('builtins.open', new_callable=MagicMock)
    @patch('tkinter.messagebox.showerror')
    def test_cat_file(self, mock_showerror, mock_open, mock_tarfile):
        # Замокаем открытие архива и файла
        mock_tarfile.return_value.__enter__.return_value.extractall = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = "File content"

        root = tk.Tk()
        emulator = ShellEmulator(root, 'virtual_fs.tar')

        # Пробуем вывести содержимое файла
        emulator.cat_file("file.txt")

        # Перехватываем вывод в текстовом поле
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            output = mock_stdout.getvalue().strip()

        # Проверяем, что содержимое файла выведено
        self.assertIn("File content", output)

        # Мокаем ошибку: файл не найден
        mock_open.side_effect = FileNotFoundError
        emulator.cat_file("missing_file.txt")

        # Перехватываем вывод в текстовом поле
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            output = mock_stdout.getvalue().strip()

        # Проверяем, что вывод содержит ошибку
        self.assertIn("Ошибка: файл 'missing_file.txt' не найден", output)

    # Тестирование выполнения команды (например, "ls")
    @patch('tkinter.messagebox.showerror')
    def test_execute_command(self, mock_showerror):
        root = tk.Tk()
        emulator = ShellEmulator(root, 'virtual_fs.tar')

        # Мокаем выполнение команды "ls"
        with patch.object(emulator, 'list_files') as mock_list_files:
            emulator.execute_command(MagicMock(get=MagicMock(return_value="ls")))
            mock_list_files.assert_called_once()

        # Тестируем неверную команду
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            emulator.execute_command(MagicMock(get=MagicMock(return_value="invalid_command")))
            output = mock_stdout.getvalue().strip()

        # Проверяем, что вывод содержит ошибку
        self.assertIn(f"{emulator.username}: команда не найдена", output)

    # Тестирование команды "touch" (создание файла)
    @patch('builtins.open', new_callable=MagicMock)
    @patch('tkinter.messagebox.showerror')
    def test_touch_file(self, mock_showerror, mock_open):
        # Мокаем открытие файла
        mock_open.return_value.__enter__.return_value = MagicMock()
        root = tk.Tk()
        emulator = ShellEmulator(root, 'virtual_fs.tar')

        # Пробуем создать файл
        emulator.touch_file("newfile.txt")

        # Перехватываем вывод в текстовом поле
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            output = mock_stdout.getvalue().strip()

        # Проверяем, что вывод содержит сообщение о создании файла
        self.assertIn("Файл 'newfile.txt' создан", output)

    # Тестирование истории команд
    @patch('tkinter.messagebox.showerror')
    def test_show_history(self, mock_showerror):
        root = tk.Tk()
        emulator = ShellEmulator(root, 'virtual_fs.tar')

        # Добавляем команды в историю
        emulator.history = ["ls", "cd dir1", "pwd"]

        # Перехватываем вывод в текстовом поле
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            emulator.show_history()
            output = mock_stdout.getvalue().strip()

        # Проверяем, что история команд выведена
        self.assertIn("ls", output)
        self.assertIn("cd dir1", output)
        self.assertIn("pwd", output)


if __name__ == "__main__":
    unittest.main()
