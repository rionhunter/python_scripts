#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox

def count_words_in_file(path):
    """Read the file and return the number of words (split on whitespace)."""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return len(text.split())

def main():
    # Hide the root window
    root = tk.Tk()
    root.withdraw()

    # Ask for a file
    file_path = filedialog.askopenfilename(
        title="Select a text or Markdown file",
        filetypes=[
            ("Text files", "*.txt"),
            ("Markdown files", "*.md"),
            ("All files", "*.*")
        ]
    )
    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected. Bye.")
        return

    # Count words and display result
    try:
        wc = count_words_in_file(file_path)
        messagebox.showinfo(
            "Word Count",
            f"'{file_path.split('/')[-1]}' contains {wc} words."
        )
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")

if __name__ == "__main__":
    main()
