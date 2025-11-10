"""
TCL transcription cleanup utility

This script provides:
- clean_transcription(text): removes speaker labels like 'Speaker1:' and collapses
  multiple blank lines while preserving paragraph breaks.
- A small Tkinter GUI to pick a text file and overwrite it with the cleaned output
  (creates a backup with .bak by default).
- A --test CLI mode to run the cleaner against a sample input and print the result.

Usage (GUI): run the script without args and use the file picker.
Usage (CLI test): python tcl_transcription_cleanup.py --test
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from typing import Tuple

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:  # pragma: no cover - GUI import on headless may fail
    tk = None


SPEAKER_RE = re.compile(r'^\s*Speaker\d+:\s*$', flags=re.IGNORECASE | re.MULTILINE)


def clean_transcription(text: str) -> str:
    """Clean TCL-style transcription text.

    Rules applied:
    - Remove lines that are only a speaker label like 'Speaker1:' (case-insensitive).
    - Remove excess newlines so each utterance appears on a single line (no empty lines).
    - Strip leading/trailing whitespace from each line and the whole text.

    Returns cleaned text with a trailing newline.
    """
    if not text:
        return "\n"
    # Normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove speaker-only lines
    text = SPEAKER_RE.sub('', text)

    # Split lines, strip each, filter out empty lines (removes excess newlines),
    # then join with a single newline so every utterance is on its own line.
    lines = [ln.strip() for ln in text.split('\n')]
    non_empty = [ln for ln in lines if ln]

    cleaned = '\n'.join(non_empty).strip() + "\n"
    return cleaned


def process_file(path: str, backup: bool = True) -> Tuple[bool, str]:
    """Read, clean and save the transcription file.

    If backup is True, create a .bak copy next to the original file.
    Returns a tuple (success, message).
    """
    if not os.path.isfile(path):
        return False, f"Input file not found: {path}"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()

        cleaned = clean_transcription(src)

        if backup:
            bak = path + '.bak'
            shutil.copy2(path, bak)

        # Write cleaned content (overwrite)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned)

        return True, f"Cleaned and saved: {path}"
    except Exception as e:
        return False, f"Error processing file: {e}"


def run_gui() -> None:
    if tk is None:
        print("Tkinter is not available in this environment.")
        return

    root = tk.Tk()
    root.title('TCL Transcription Cleanup')
    root.geometry('480x140')

    input_var = tk.StringVar()
    backup_var = tk.BooleanVar(value=True)

    def choose_file():
        p = filedialog.askopenfilename(title='Select transcription TXT file',
                                       filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if p:
            input_var.set(p)

    def do_process():
        path = input_var.get().strip()
        if not path:
            messagebox.showwarning('No file', 'Please select a file first.')
            return
        ok, msg = process_file(path, backup=backup_var.get())
        if ok:
            messagebox.showinfo('Success', msg)
        else:
            messagebox.showerror('Error', msg)

    frame = tk.Frame(root, padx=12, pady=12)
    frame.pack(fill='both', expand=True)

    tk.Label(frame, text='Transcription TXT file:').grid(row=0, column=0, sticky='w')
    tk.Entry(frame, textvariable=input_var, width=50).grid(row=1, column=0, columnspan=2, sticky='we')
    tk.Button(frame, text='Browse...', command=choose_file).grid(row=1, column=2, padx=6)

    tk.Checkbutton(frame, text='Create .bak backup', variable=backup_var).grid(row=2, column=0, sticky='w', pady=8)

    tk.Button(frame, text='Clean and Save', command=do_process, width=20).grid(row=3, column=0, pady=6)
    tk.Button(frame, text='Quit', command=root.destroy, width=10).grid(row=3, column=2, pady=6)

    root.mainloop()


def _test_sample() -> None:
    sample = (
        "Speaker1:\nWhere was the life stored?\n\nSpeaker1:\nHow did he continue to exist?\n\n"
        "Speaker1:\nWhat did it take for him to regrow?\n\nSpeaker1:\nHow little could he regrow from?  \n"
    )
    print('=== Original ===')
    print(sample)
    print('=== Cleaned ===')
    print(clean_transcription(sample))


def main(argv=None):
    parser = argparse.ArgumentParser(description='TCL transcription cleanup utility')
    parser.add_argument('--test', action='store_true', help='Run built-in test and exit')
    parser.add_argument('--input', '-i', help='Input file to clean (overwrites)')
    parser.add_argument('--no-backup', action='store_true', help='Do not create .bak backup')
    args = parser.parse_args(argv)

    if args.test:
        _test_sample()
        return 0

    if args.input:
        ok, msg = process_file(args.input, backup=not args.no_backup)
        print(msg)
        return 0 if ok else 2

    # No args -> run GUI
    run_gui()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
