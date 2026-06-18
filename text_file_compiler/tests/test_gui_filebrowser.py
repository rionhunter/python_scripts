import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication

from gui.main_window import FileBrowser, MainWindow
from settings.config import Config
from core.file_processor import FileProcessor


_QAPP = None


def get_qapp():
    global _QAPP
    if _QAPP is None:
        _QAPP = QApplication(sys.argv[:1])
    return _QAPP


class FileBrowserTests(unittest.TestCase):
    def setUp(self):
        # Ensure offscreen rendering is used in CI/HEADLESS
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        self.app = get_qapp()

    def test_directory_and_file_rows_use_single_title_line(self):
        with tempfile.TemporaryDirectory() as td:
            root = td
            # Create directory and files
            os.makedirs(os.path.join(root, 'subdir', 'nested'), exist_ok=True)
            f1 = os.path.join(root, 'subdir', 'a.txt')
            f2 = os.path.join(root, 'b.txt')
            with open(f1, 'w', encoding='utf-8') as fh:
                fh.write('hello')
            with open(f2, 'w', encoding='utf-8') as fh:
                fh.write('world')

            cfg = Config()
            cfg.set_last_directory(root)
            fb = FileBrowser(cfg)
            fb.current_directory = root
            fb.populate_tree()

            dir_path = os.path.join(root, 'subdir')
            card = fb._path_to_card.get(dir_path)
            self.assertIsNotNone(card, 'Directory card not found')
            self.assertEqual(card.title_label.text(), 'subdir')
            self.assertIsNone(card.subtitle_label)

            file_card = fb._path_to_card.get(f1)
            self.assertIsNotNone(file_card, 'File card not found')
            self.assertEqual(file_card.title_label.text(), 'a.txt')
            self.assertIsNone(file_card.subtitle_label)

    def test_window_geometry_is_clamped_into_target_screen(self):
        screen = QRect(1920, 0, 1920, 1080)
        saved = QRect(100, 100, 1400, 900)

        normalized = MainWindow._normalize_rect_for_screen(saved, screen, force_to_screen=True)

        self.assertTrue(screen.contains(normalized.center()))
        self.assertGreaterEqual(normalized.left(), screen.left())
        self.assertGreaterEqual(normalized.top(), screen.top())
        self.assertLessEqual(normalized.right(), screen.right())
        self.assertLessEqual(normalized.bottom(), screen.bottom())

    def test_navigate_to_parent_directory_ignores_unset_browser_path(self):
        browser = SimpleNamespace(current_directory=None, navigate_to=mock.Mock())
        path_edit = mock.Mock()
        path_edit.text.return_value = ""
        window = SimpleNamespace(file_browser=browser, path_edit=path_edit)

        MainWindow.navigate_to_parent_directory(window)

        browser.navigate_to.assert_not_called()

    def test_navigate_to_parent_directory_uses_parent_of_current_directory(self):
        with tempfile.TemporaryDirectory() as td:
            child = os.path.join(td, 'child')
            os.makedirs(child, exist_ok=True)

            browser = SimpleNamespace(current_directory=child, navigate_to=mock.Mock())
            path_edit = mock.Mock()
            path_edit.text.return_value = child
            window = SimpleNamespace(file_browser=browser, path_edit=path_edit)

            MainWindow.navigate_to_parent_directory(window)

            browser.navigate_to.assert_called_once_with(os.path.abspath(td))


if __name__ == '__main__':
    unittest.main()
