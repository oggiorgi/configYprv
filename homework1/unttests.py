import unittest
import os
import tarfile
from emulator import ShellEmulator
from tkinter import Tk

class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаём виртуальную файловую систему для тестов
        cls.virtual_fs_path = "test_fs.tar.gz"
        with tarfile.open(cls.virtual_fs_path, "w:gz") as tar:
            os.mkdir("test_fs")
            with open("test_fs/test_file.txt", "w") as f:
                f.write("test content")
            tar.add("test_fs", arcname="/")
            os.remove("test_fs/test_file.txt")
            os.rmdir("test_fs")

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.virtual_fs_path)
        if os.path.exists("virtual_fs"):
            for root, dirs, files in os.walk("virtual_fs", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir("virtual_fs")

    def setUp(self):
        self.root = Tk()
        self.emulator = ShellEmulator(self.root, "test_user", self.virtual_fs_path)

    def tearDown(self):
        self.root.destroy()

    def test_extract_virtual_fs(self):
        self.emulator.extract_virtual_fs()
        self.assertTrue(os.path.exists("virtual_fs"))

    def test_list_files(self):
        self.emulator.extract_virtual_fs()
        self.emulator.list_files()
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertIn("test_file.txt", output)

    def test_print_working_directory(self):
        self.emulator.print_working_directory()
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertEqual(output, "test_user:/")

    def test_touch_file(self):
        self.emulator.extract_virtual_fs()
        self.emulator.touch_file("new_file.txt")
        self.assertTrue(os.path.exists("virtual_fs/new_file.txt"))

    def test_touch_file_error(self):
        self.emulator.current_path = "/nonexistent_path"
        self.emulator.touch_file("file.txt")
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertIn("Ошибка при создании файла", output)

    def test_chmod_file(self):
        self.emulator.extract_virtual_fs()
        self.emulator.touch_file("chmod_test.txt")
        self.emulator.chmod_file("777 chmod_test.txt")
        self.assertTrue(os.access("virtual_fs/chmod_test.txt", os.W_OK))

    def test_chmod_file_not_found(self):
        self.emulator.chmod_file("777 nonexistent_file.txt")
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertIn("Файл не найден", output)

    def test_ls_empty_directory(self):
        os.mkdir("virtual_fs/empty_dir")
        self.emulator.change_directory("empty_dir")
        self.emulator.list_files()
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertEqual(output, "Пустая директория")

    def test_execute_command_ls(self):
        self.emulator.extract_virtual_fs()
        self.emulator.entry.insert(0, "ls")
        self.emulator.execute_command(None)
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertIn("test_file.txt", output)

    def test_execute_command_invalid(self):
        self.emulator.entry.insert(0, "invalid_cmd")
        self.emulator.execute_command(None)
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertIn("команда не найдена", output)

    def test_execute_command_touch(self):
        self.emulator.entry.insert(0, "touch new_test_file.txt")
        self.emulator.execute_command(None)
        self.assertTrue(os.path.exists("virtual_fs/new_test_file.txt"))

    def test_execute_command_pwd(self):
        self.emulator.entry.insert(0, "pwd")
        self.emulator.execute_command(None)
        output = self.emulator.text_area.get("1.0", "end").strip()
        self.assertIn("test_user:/", output)

if __name__ == "__main__":
    unittest.main()
