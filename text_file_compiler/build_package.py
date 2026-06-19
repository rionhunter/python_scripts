"""Cross-platform packaging script for Text File Compiler."""

import argparse
import os
from pathlib import Path


def build_args(onefile: bool) -> list[str]:
    path_sep = ";" if os.name == "nt" else ":"
    root = Path(__file__).resolve().parent

    args = [
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "TextFileCompiler",
        "--collect-all",
        "PyQt6",
        "--add-data",
        f"{root / 'demo_files'}{path_sep}demo_files",
        "--add-data",
        f"{root / 'README.md'}{path_sep}.",
        str(root / "main.py"),
    ]

    if onefile:
        args.insert(2, "--onefile")

    return args


def main() -> int:
    parser = argparse.ArgumentParser(description="Build distributable binaries with PyInstaller")
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build a single-file executable (slower startup, easier distribution)",
    )
    args = parser.parse_args()

    from PyInstaller.__main__ import run

    run(build_args(onefile=args.onefile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
