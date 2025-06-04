import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pyperclip

class FileCollectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Collector")

        self.file_list = []
        self.blacklist = []
        self.project_context = self.load_project_context()

        self.load_file_list()
        self.load_blacklist()

        self.create_widgets()
        self.scan_directory()  # Automatically scan the directory at startup

    def create_widgets(self):
        self.context_frame = tk.Frame(self.root)
        self.context_frame.pack(fill=tk.X)

        self.context_label = tk.Label(self.context_frame, text="Project Context:")
        self.context_label.pack(side=tk.LEFT)

        self.context_entry = tk.Entry(self.context_frame, width=100)
        self.context_entry.pack(fill=tk.X, expand=True)
        self.context_entry.insert(0, self.project_context)

        self.file_frame = tk.Frame(self.root)
        self.file_frame.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(self.file_frame, selectmode=tk.SINGLE)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar = tk.Scrollbar(self.file_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.file_listbox.yview)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X)

        self.add_button = tk.Button(self.button_frame, text="Add File", command=self.add_file)
        self.add_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_file)
        self.delete_button.pack(side=tk.LEFT)

        self.move_up_button = tk.Button(self.button_frame, text="Move Up", command=self.move_up)
        self.move_up_button.pack(side=tk.LEFT)

        self.move_down_button = tk.Button(self.button_frame, text="Move Down", command=self.move_down)
        self.move_down_button.pack(side=tk.LEFT)

        self.compile_button = tk.Button(self.button_frame, text="Compile", command=self.compile_files)
        self.compile_button.pack(side=tk.RIGHT)

        self.blacklist_frame = tk.Frame(self.root)
        self.blacklist_frame.pack(fill=tk.BOTH, expand=True)

        self.blacklist_label = tk.Label(self.blacklist_frame, text="Blacklist:")
        self.blacklist_label.pack(side=tk.TOP, anchor="w")

        self.blacklist_listbox = tk.Listbox(self.blacklist_frame, selectmode=tk.SINGLE)
        self.blacklist_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar_blacklist = tk.Scrollbar(self.blacklist_frame)
        self.scrollbar_blacklist.pack(side=tk.RIGHT, fill=tk.Y)

        self.blacklist_listbox.config(yscrollcommand=self.scrollbar_blacklist.set)
        self.scrollbar_blacklist.config(command=self.blacklist_listbox.yview)

        self.blacklist_button_frame = tk.Frame(self.blacklist_frame)
        self.blacklist_button_frame.pack(fill=tk.X)

        self.add_blacklist_button = tk.Button(self.blacklist_button_frame, text="Add to Blacklist", command=self.add_to_blacklist)
        self.add_blacklist_button.pack(side=tk.LEFT)

        self.delete_blacklist_button = tk.Button(self.blacklist_button_frame, text="Remove from Blacklist", command=self.remove_from_blacklist)
        self.delete_blacklist_button.pack(side=tk.LEFT)

        self.compiled_frame = tk.Frame(self.root)
        self.compiled_frame.pack(fill=tk.BOTH, expand=True)

        self.compiled_text = tk.Text(self.compiled_frame, wrap=tk.WORD)
        self.compiled_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar_compiled = tk.Scrollbar(self.compiled_frame)
        self.scrollbar_compiled.pack(side=tk.RIGHT, fill=tk.Y)

        self.compiled_text.config(yscrollcommand=self.scrollbar_compiled.set)
        self.scrollbar_compiled.config(command=self.compiled_text.yview)

        self.copy_button = tk.Button(self.button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.RIGHT)

        self.update_listbox()
        self.update_blacklistbox()

    def add_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_list.append(file_path)
            self.update_listbox()
            self.save_file_list()

    def delete_file(self):
        selected = self.file_listbox.curselection()
        if selected:
            self.file_list.pop(selected[0])
            self.update_listbox()
            self.save_file_list()

    def move_up(self):
        selected = self.file_listbox.curselection()
        if selected and selected[0] > 0:
            idx = selected[0]
            self.file_list[idx], self.file_list[idx - 1] = self.file_list[idx - 1], self.file_list[idx]
            self.update_listbox()
            self.file_listbox.select_set(idx - 1)
            self.save_file_list()

    def move_down(self):
        selected = self.file_listbox.curselection()
        if selected and selected[0] < len(self.file_list) - 1:
            idx = selected[0]
            self.file_list[idx], self.file_list[idx + 1] = self.file_list[idx + 1], self.file_list[idx]
            self.update_listbox()
            self.file_listbox.select_set(idx + 1)
            self.save_file_list()

    def add_to_blacklist(self):
        path = filedialog.askopenfilename() or filedialog.askdirectory()
        if path:
            self.blacklist.append(os.path.normpath(path))
            self.update_blacklistbox()
            self.save_blacklist()
            self.scan_directory()  # Rescan directory to update file tree

    def remove_from_blacklist(self):
        selected = self.blacklist_listbox.curselection()
        if selected:
            self.blacklist.pop(selected[0])
            self.update_blacklistbox()
            self.save_blacklist()
            self.scan_directory()  # Rescan directory to update file tree

    def save_file_list(self):
        with open("file_list.txt", "w") as file:
            for path in self.file_list:
                file.write(path + "\n")

    def load_file_list(self):
        if os.path.exists("file_list.txt"):
            with open("file_list.txt", "r") as file:
                self.file_list = [line.strip() for line in file.readlines()]

    def save_blacklist(self):
        with open("blacklist.txt", "w") as file:
            for path in self.blacklist:
                file.write(path + "\n")

    def load_blacklist(self):
        if os.path.exists("blacklist.txt"):
            with open("blacklist.txt", "r") as file:
                self.blacklist = [line.strip() for line in file.readlines()]

    def save_project_context(self):
        with open("project_context.txt", "w") as file:
            file.write(self.context_entry.get())

    def load_project_context(self):
        if os.path.exists("project_context.txt"):
            with open("project_context.txt", "r") as file:
                return file.read()
        return ""

    def scan_directory(self):
        # Scan the directory where the script is located
        directory = os.path.dirname(os.path.abspath(__file__))
        self.file_tree = self.create_file_tree(directory)

    def update_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for path in self.file_list:
            self.file_listbox.insert(tk.END, path)

    def update_blacklistbox(self):
        self.blacklist_listbox.delete(0, tk.END)
        for path in self.blacklist:
            self.blacklist_listbox.insert(tk.END, path)

    def compile_files(self):
        project_context = self.context_entry.get()
        self.save_project_context()

        compiled_text = f"Project Context:\n{project_context}\n\nFile Tree:\n{self.file_tree}\n\n"

        for file_path in self.file_list:
            try:
                with open(file_path, "r") as file:
                    file_content = file.read()
                    compiled_text += f"\n\n# File: {file_path}\n\n{file_content}\n"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read {file_path}.\nError: {e}")
                return

        self.compiled_text.delete(1.0, tk.END)
        self.compiled_text.insert(tk.END, compiled_text)

    def create_file_tree(self, root_dir):
        file_tree = ""
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not self.is_blacklisted(os.path.join(root, d))]
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            file_tree += f"{indent}{os.path.basename(root)}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                file_path = os.path.join(root, f)
                if not self.is_blacklisted(file_path):
                    file_tree += f"{subindent}{f}\n"
        return file_tree

    def is_blacklisted(self, path):
        normalized_path = os.path.normpath(path)
        for blacklist_path in self.blacklist:
            if normalized_path.startswith(os.path.normpath(blacklist_path)):
                return True
        return False

    def copy_to_clipboard(self):
        compiled_text = self.compiled_text.get(1.0, tk.END)
        pyperclip.copy(compiled_text)
        messagebox.showinfo("Copied", "Compiled text copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCollectorApp(root)
    root.mainloop()
