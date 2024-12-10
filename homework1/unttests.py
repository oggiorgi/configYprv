import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):

    @patch('tarfile.open')  # Мокируем tarfile.open
    @patch.object(ShellEmulator, 'extract_virtual_fs')  # Мокируем метод extract_virtual_fs
    def setUp(self, mock_extract, mock_tarfile):
        """Инициализация ShellEmulator для каждого теста."""
        # Заглушка для extract_virtual_fs, чтобы не пытаться извлечь файл
        mock_extract.return_value = None

        # Заглушка для tarfile.open
        mock_tarfile.return_value.__enter__.return_value.extractall = MagicMock()

        # Создаем эмулятор
        self.root = tk.Tk()
        self.emulator = ShellEmulator(self.root, "test_user", "test_virtual_fs.tar")

    @patch('os.listdir')
    def test_list_files(self, mock_listdir):
        """Тест команды 'ls'."""
        # Мокаем список файлов
        mock_listdir.return_value = ["file1.txt", "file2.txt"]

        # Выполняем команду
        with patch.object(self.emulator.text_area, 'insert') as mock_insert:
            self.emulator.list_files()

        # Проверяем, что имена файлов выведены
        mock_insert.assert_called_with(tk.END, "file1.txt\nfile2.txt\n")

    @patch('os.path.isdir')
    def test_change_directory(self, mock_isdir):
        """Тест команды 'cd'."""
        # Мокаем существующую директорию
        mock_isdir.return_value = True

        # Меняем директорию
        self.emulator.change_directory("dir1")
        self.assertEqual(self.emulator.current_path, "/dir1")

        # Проверяем несуществующую директорию
        mock_isdir.return_value = False
        with patch.object(self.emulator.text_area, 'insert') as mock_insert:
            self.emulator.change_directory("invalid_dir")
            mock_insert.assert_called_with(tk.END, "Директория не найдена\n")

    def test_print_working_directory(self):
        """Тест команды 'pwd'."""
        with patch.object(self.emulator.text_area, 'insert') as mock_insert:
            self.emulator.print_working_directory()
            mock_insert.assert_called_with(tk.END, "test_user:/\n")

    @patch('builtins.open', new_callable=MagicMock)
    def test_touch_file(self, mock_open):
        """Тест команды 'touch'."""
        # Создаём файл
        with patch.object(self.emulator.text_area, 'insert') as mock_insert:
            self.emulator.touch_file("newfile.txt")
            mock_insert.assert_called_with(tk.END, "Файл 'newfile.txt' создан.\n")

    @patch('os.chmod')
    def test_chmod_file(self, mock_chmod):
        """Тест команды 'chmod'."""
        # Успешное изменение прав
        with patch.object(self.emulator.text_area, 'insert') as mock_insert:
            self.emulator.chmod_file("777 newfile.txt")
            mock_insert.assert_called_with(tk.END, "Права для файла newfile.txt изменены на 777\n")

        # Ошибка при изменении прав
        mock_chmod.side_effect = FileNotFoundError
        with patch.object(self.emulator.text_area, 'insert') as mock_insert:
            self.emulator.chmod_file("777 missing_file.txt")
            mock_insert.assert_called_with(tk.END, "Файл не найден\n")


if __name__ == "__main__":
    unittest.main()
