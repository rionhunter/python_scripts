import re
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def remove_citations_from_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove citations and any preceding whitespace or punctuation
    # Remove citations and any preceding whitespace or punctuation, but preserve newlines
    cleaned = re.sub(r'(\s?[.])?\s*\[\\?\[\d+\\?\]\]\([^)]*\)', '', content)
    # Remove leftover double spaces and fix spacing after removal
    cleaned = re.sub(r' +', ' ', cleaned)
    cleaned = re.sub(r' +\n', '\n', cleaned)
    # Do not collapse blank lines
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

def select_file_and_process():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title='Select Markdown File',
        filetypes=[('Markdown files', '*.md'), ('All files', '*.*')]
    )
    if not file_path:
        return
    try:
        remove_citations_from_markdown(file_path)
        messagebox.showinfo('Success', f'Citations removed from {os.path.basename(file_path)}')
    except Exception as e:
        messagebox.showerror('Error', str(e))

if __name__ == '__main__':
    select_file_and_process()
