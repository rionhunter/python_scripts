import os
import sys
import tempfile
import unittest

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow
from core.file_processor import FileProcessor


_QAPP = None


def get_qapp():
    global _QAPP
    if _QAPP is None:
        _QAPP = QApplication(sys.argv[:1])
    return _QAPP


class CompileOrderInclusionTests(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        self.app = get_qapp()

    def test_toggling_single_file_updates_project_files(self):
        with tempfile.TemporaryDirectory() as td:
            fpath = os.path.join(td, 'sample.txt')
            with open(fpath, 'w', encoding='utf-8') as fh:
                fh.write('hello')

            win = MainWindow()

            # Simulate user toggling the file checkbox on
            win.on_browser_selection_toggled(fpath, False, True)
            self.assertIn(fpath, win.project_files)

            # Now toggle off
            win.on_browser_selection_toggled(fpath, False, False)
            self.assertNotIn(fpath, win.project_files)

    def test_toggling_directory_includes_subdirectory_files(self):
        with tempfile.TemporaryDirectory() as td:
            # Create files in natural numeric order
            names = ["chapter10.md", "chapter2.md", "chapter1.md"]
            for n in names:
                with open(os.path.join(td, n), 'w', encoding='utf-8') as fh:
                    fh.write(n)

            expected = FileProcessor.collect_text_files(td, recursive=False)
            self.assertEqual(
                [os.path.basename(p) for p in expected],
                [os.path.basename(p) for p in sorted(expected, key=lambda s: FileProcessor.natural_sort_key(os.path.basename(s)))],
            )

            win = MainWindow()
            # Ensure include_subdirectories flag is False for this test (we created files in root)
            win.include_subdirectories_enabled = False

            win.on_browser_selection_toggled(td, True, True)
            # After toggling directory, project_files should contain the collected text files
            self.assertEqual(sorted(win.project_files), sorted(expected))

    def test_partial_directory_toggle_can_remove_all_descendants(self):
        with tempfile.TemporaryDirectory() as td:
            left = os.path.join(td, 'a.txt')
            right = os.path.join(td, 'b.txt')
            for path in (left, right):
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(path)

            win = MainWindow()
            win.include_subdirectories_enabled = False
            win.file_browser.navigate_to(td)

            win.add_files_to_project([left])
            directory_card = win.file_browser._path_to_card[td]
            self.assertEqual(directory_card.check_state(), Qt.CheckState.PartiallyChecked)

            directory_card.progress_toggle.click()

            self.assertEqual(win.project_files, [])
            self.assertEqual(directory_card.check_state(), Qt.CheckState.Unchecked)


if __name__ == '__main__':
    unittest.main()
