import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.root = None  # Не будем запускать GUI в тестах
        self.emulator = ShellEmulator(None, "test_user", "virtual_fs.tar")

    @patch('os.listdir', return_value=['file1.txt', 'file2.txt'])
    def test_ls(self, mock_listdir):
        self.emulator.list_files()
        self.assertIn("file1.txt", self.emulator.text_area.get("1.0", "end"))

    @patch('os.path.isdir', return_value=True)
    def test_cd(self, mock_isdir):
        self.emulator.change_directory("subdir")
        self.assertEqual(self.emulator.current_path, "/subdir")

    def test_touch(self):
        with patch("builtins.open", mock_open()) as mock_file:
            self.emulator.touch_file("newfile.txt")
            mock_file.assert_called_once_with("virtual_fs/newfile.txt", 'a')

    @patch('os.chmod')
    def test_chmod(self, mock_chmod):
        self.emulator.change_permissions("644 file.txt")
        mock_chmod.assert_called_once()

if __name__ == "__main__":
    unittest.main()
