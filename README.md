Launch scripts
- GUI (PowerShell): powershell -ExecutionPolicy Bypass -File launchers\launch_dynamic_replacer_gui.ps1
- GUI (Batch): launchers\launch_dynamic_replacer_gui.bat
- Test: launchers\launch_dynamic_replacer_test.bat
- Bash (POSIX): bash launchers/launch_dynamic_replacer.sh
# python_scripts
A collection of assorted helper scripts used across various projects.
The tools range from quick text utilities to experiments with Blender
and GUI helpers.

## Root scripts
- `bad_text_scanner.py` – scan a directory for files that fail UTF‑8 encoding.
- `clipboard_cvs_to_array.py` – convert comma separated clipboard text to a Python list.
- `clipboard_lines_to_string_array.py` – split clipboard lines into a list.
- `clipboard_text_replacer.py` – GUI tool for replacing text in the clipboard.
- `deprinter.py` – recursively remove lines starting with `print(` from files.
- `ghost_print_remover.py` – strip commented out print statements.
- `launcher.py` – PyQt6 interface for launching scripts.
- `launcher_a.py` – alternate launcher interface.
- `linux_compatibility.py` – add shebangs and permissions for running on Linux.
- `list_orderer.py` – renumber lines from the clipboard sequentially.
- `scan.py` – search files for a phrase and show matches.
- `scriptboard.py` – Tkinter board listing scripts in the current folder.
- `shortcut_text_formatter.py` – format shortcut strings with colons.

## Directory overview
- `blender/` – automation and generation scripts for Blender.
- `command_line/` – command‑line argument experiments.
- `data_management/` – helpers for managing text and dictionaries.
- `document_builders/` – utilities for generating documents or PDFs.
- `experiments/` – assorted prototypes and scratch work.
- `gatherers/` – scripts that collect data from files or the web.
- `git_manager/` – small Tkinter tool for handling git repositories.
- `godot_augment/` – utilities for working with the Godot engine.
- `gpt_augment/` – helpers that integrate GPT based features.
- `GPU/` – simple GPU detection scripts for Blender.
- `HUD/` – overlay and heads‑up display utilities.
- `image_alteration/` – tools for cropping, scaling and processing images.
- `audio_editing/` – simple audio trimming and conversion utilities.
- `maths/` – quick math helpers.
- `recording/` – screen capture and timelapse utilities.
- `text_editing/` – text manipulation scripts.
- `typing_augment/` – keyboard automation experiments.
- `utils/` – reusable utility modules (see below).
- `youtube/` – helpers for working with YouTube content.

## Utilities layout
Scripts are organized under `utils/`:
- `text_utils` contains text manipulation helpers.
- `file_utils` includes file management scripts.
- `image_utils` groups image conversion tools.

See each folder for more details and additional utilities.
