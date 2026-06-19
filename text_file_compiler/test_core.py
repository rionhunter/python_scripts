"""Automated tests for the text file compiler."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main
from core.compiler import Compiler
from core.file_processor import FileProcessor
from settings.config import Config, ProjectConfig


class FileProcessorTests(unittest.TestCase):
    def test_format_file_size(self):
        self.assertEqual(FileProcessor.format_file_size(0), "0 B")
        self.assertEqual(FileProcessor.format_file_size(1024), "1.0 KB")
        self.assertEqual(FileProcessor.format_file_size(1048576), "1.0 MB")

    def test_is_text_file_detects_text_and_binary_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            text_path = Path(temp_dir) / "sample.custom"
            binary_path = Path(temp_dir) / "sample.bin"

            text_path.write_text("plain text content", encoding="utf-8")
            binary_path.write_bytes(b"\x00\x01\x02")

            self.assertTrue(FileProcessor.is_text_file(str(text_path)))
            self.assertFalse(FileProcessor.is_text_file(str(binary_path)))

    def test_scan_directory_excludes_hidden_items_and_sorts_directories_first(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "visible_dir").mkdir()
            (root / "visible_file.txt").write_text("hello", encoding="utf-8")
            (root / ".hidden.txt").write_text("secret", encoding="utf-8")

            items = FileProcessor.scan_directory(str(root))

            self.assertEqual([item["name"] for item in items], ["visible_dir", "visible_file.txt"])
            self.assertTrue(items[0]["is_directory"])
            self.assertFalse(items[1]["is_directory"])

    def test_collect_text_files_uses_natural_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "chapter10.md").write_text("ten", encoding="utf-8")
            (root / "chapter2.md").write_text("two", encoding="utf-8")
            (root / "chapter1.md").write_text("one", encoding="utf-8")

            files = FileProcessor.collect_text_files(str(root), recursive=False)

            self.assertEqual(
                [Path(file_path).name for file_path in files],
                ["chapter1.md", "chapter2.md", "chapter10.md"],
            )


class CompilerTests(unittest.TestCase):
    def test_compile_files_includes_header_tree_and_content(self):
        compiler = Compiler()

        with tempfile.TemporaryDirectory() as temp_dir:
            first_file = Path(temp_dir) / "test1.py"
            second_file = Path(temp_dir) / "notes.md"
            first_file.write_text('print("Hello")\n', encoding="utf-8")
            second_file.write_text("# Notes\n\nBody\n", encoding="utf-8")

            output = compiler.compile_files(
                [str(first_file), str(second_file)],
                {
                    "name": "Test Project",
                    "description": "Compilation test",
                    "output_settings": {
                        "include_file_names": True,
                        "include_file_tree": True,
                    },
                },
            )

            self.assertIn("# Test Project", output)
            self.assertIn("Compilation test", output)
            self.assertIn("## File Structure", output)
            self.assertIn("test1.py", output)
            self.assertIn("notes.md", output)
            self.assertIn('print("Hello")', output)
            self.assertIn("# Notes", output)
            self.assertNotIn("```", output)

    def test_compile_files_can_remove_trailing_whitespace(self):
        compiler = Compiler()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "trailing.txt"
            file_path.write_text("alpha   \n beta\t\t\nkept\n", encoding="utf-8")

            output = compiler.compile_files(
                [str(file_path)],
                {
                    "name": "Trim Project",
                    "output_settings": {
                        "include_file_names": False,
                        "include_file_tree": False,
                        "remove_trailing_whitespace": True,
                    },
                },
            )

            content_section = output.split("---\n\n", 1)[1].split("\n\n---", 1)[0]
            self.assertEqual(content_section.splitlines(), ["", "alpha", " beta", "kept", ""])
            self.assertNotIn("alpha   ", output)
            self.assertNotIn(" beta\t\t", output)

    def test_compile_files_reports_missing_files(self):
        compiler = Compiler()
        missing_file = os.path.join(tempfile.gettempdir(), "definitely_missing_file.txt")

        output = compiler.compile_files(
            [missing_file],
            {
                "name": "Missing File Project",
                "output_settings": {
                    "include_file_names": True,
                    "include_file_tree": False,
                },
            },
        )

        self.assertIn("File not found", output)
        self.assertIn(missing_file, output)

    def test_get_compilation_stats_counts_missing_and_binary_files(self):
        compiler = Compiler()

        with tempfile.TemporaryDirectory() as temp_dir:
            text_file = Path(temp_dir) / "sample.txt"
            binary_file = Path(temp_dir) / "sample.bin"
            text_file.write_text("abc", encoding="utf-8")
            binary_file.write_bytes(b"\x00\x01")
            missing_file = str(Path(temp_dir) / "missing.txt")

            stats = compiler.get_compilation_stats([str(text_file), str(binary_file), missing_file])

            self.assertEqual(stats["total_files"], 3)
            self.assertEqual(stats["text_files"], 1)
            self.assertEqual(stats["binary_files"], 1)
            self.assertEqual(stats["missing_files"], 1)


class ProjectConfigTests(unittest.TestCase):
    def test_project_config_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = os.path.join(temp_dir, "project.json")
            config = ProjectConfig(project_file)

            config.set_name("Test Project")
            config.set_description("A project used in tests")
            config.add_file("first.py")
            config.add_file("second.md")
            config.set_browser_location(temp_dir)
            config.set_output_settings({
                "include_file_names": False,
                "include_file_tree": True,
                "remove_trailing_whitespace": True,
            })
            config.save_project()

            reloaded = ProjectConfig(project_file)

            self.assertEqual(reloaded.get_name(), "Test Project")
            self.assertEqual(reloaded.get_description(), "A project used in tests")
            self.assertEqual(reloaded.get_files(), ["first.py", "second.md"])
            self.assertEqual(reloaded.get_browser_location(), temp_dir)
            self.assertEqual(
                reloaded.get_output_settings(),
                {
                    "include_file_names": False,
                    "include_file_tree": True,
                    "remove_trailing_whitespace": True,
                },
            )


class ConfigPreferenceTests(unittest.TestCase):
    def test_preference_setters_write_expected_keys(self):
        config = Config()

        with mock.patch.object(config, "set_value") as set_value:
            config.set_auto_populate_enabled(False)
            config.set_exclude_empty_enabled(False)
            config.set_file_filter_text("notes")
            config.set_file_sort_mode("Path ↓")
            config.set_remove_trailing_whitespace_enabled(True)

        set_value.assert_any_call("ui/auto_populate_enabled", False)
        set_value.assert_any_call("ui/exclude_empty_enabled", False)
        set_value.assert_any_call("ui/file_filter_text", "notes")
        set_value.assert_any_call("ui/file_sort_mode", "Path ↓")
        set_value.assert_any_call("ui/remove_trailing_whitespace_enabled", True)

    def test_preference_getters_request_expected_keys_and_defaults(self):
        config = Config()
        lookup = {
            "ui/auto_populate_enabled": True,
            "ui/exclude_empty_enabled": True,
            "ui/file_filter_text": "",
            "ui/file_sort_mode": "Name ↑",
            "ui/remove_trailing_whitespace_enabled": False,
        }

        def fake_get_value(key, default, value_type):
            self.assertIn(key, lookup)
            self.assertEqual(default, lookup[key])
            return default

        with mock.patch.object(config, "get_value", side_effect=fake_get_value):
            self.assertTrue(config.get_auto_populate_enabled())
            self.assertTrue(config.get_exclude_empty_enabled())
            self.assertEqual(config.get_file_filter_text(), "")
            self.assertEqual(config.get_file_sort_mode(), "Name ↑")
            self.assertFalse(config.get_remove_trailing_whitespace_enabled())


class MainEntryPointTests(unittest.TestCase):
    def test_check_dependencies_returns_false_when_a_module_is_missing(self):
        original_import_module = main.importlib.import_module

        def fake_import_module(module_name):
            if module_name == "chardet":
                raise ImportError("missing chardet")
            return original_import_module(module_name)

        with mock.patch.object(main.importlib, "import_module", side_effect=fake_import_module):
            self.assertFalse(main.check_dependencies())

    def test_parse_args_understands_smoke_test_flags(self):
        args = main.parse_args(["--check", "--offscreen"])

        self.assertTrue(args.check)
        self.assertTrue(args.offscreen)

    def test_configure_qt_font_directory_uses_first_existing_candidate(self):
        fake_pyqt_module = mock.Mock()
        fake_pyqt_module.__file__ = r"C:\\fake\\site-packages\\PyQt6\\__init__.py"
        first_candidate = r"C:\\fake\\site-packages\\PyQt6\\Qt6\\lib\\fonts"

        def fake_isdir(path):
            return os.path.normcase(os.path.normpath(path)) == os.path.normcase(os.path.normpath(first_candidate))

        with mock.patch.dict(main.os.environ, {}, clear=True), mock.patch.object(
            main.importlib, "import_module", return_value=fake_pyqt_module
        ), mock.patch.object(main.os.path, "isdir", side_effect=fake_isdir):
            main.configure_qt_font_directory()
            self.assertEqual(
                os.path.normcase(os.path.normpath(main.os.environ.get("QT_QPA_FONTDIR", ""))),
                os.path.normcase(os.path.normpath(first_candidate)),
            )

    def test_configure_qt_font_directory_does_not_override_existing_setting(self):
        with mock.patch.dict(main.os.environ, {"QT_QPA_FONTDIR": "already-set"}, clear=True):
            main.configure_qt_font_directory()
            self.assertEqual(main.os.environ.get("QT_QPA_FONTDIR"), "already-set")

    def test_run_startup_check_uses_application_factory_and_window_class(self):
        app = mock.Mock()
        window = mock.Mock()
        main_window_class = mock.Mock(return_value=window)

        with mock.patch.object(main, "create_application", return_value=app), mock.patch.object(
            main, "resolve_main_window_class", return_value=main_window_class
        ):
            exit_code = main.run_startup_check(offscreen=True)

        self.assertEqual(exit_code, 0)
        main_window_class.assert_called_once_with()
        window.close.assert_called_once_with()
        app.quit.assert_called_once_with()


class LaunchScriptTests(unittest.TestCase):
    def test_batch_launcher_uses_local_venv_and_passes_arguments(self):
        script_path = Path(__file__).with_name("launch_python_main.bat")
        script_text = script_path.read_text(encoding="utf-8")

        self.assertIn('.venv\\Scripts\\python.exe', script_text)
        self.assertIn('%*', script_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)