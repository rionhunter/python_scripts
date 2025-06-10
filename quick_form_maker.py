#!/usr/bin/env python3
"""Interactive form builder for generating text documents."""

import importlib
import os
import tkinter as tk
from tkinter import filedialog, messagebox

MODULE_DIR = os.path.join(os.path.dirname(__file__), "document_builders", "form_modules")


class FormMaker(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Quick Form Maker")
        self.available_modules = self.load_modules()
        self.components = []

        self.module_var = tk.StringVar(self)
        if self.available_modules:
            self.module_var.set(self.available_modules[0].name)
        tk.OptionMenu(self, self.module_var, *[m.name for m in self.available_modules]).pack(fill="x")
        tk.Button(self, text="Add Component", command=self.add_component).pack(fill="x")

        self.component_frame = tk.Frame(self)
        self.component_frame.pack(fill="both", expand=True)

        tk.Button(self, text="Generate Output", command=self.generate_output).pack(fill="x")
        self.output_text = tk.Text(self, height=10)
        self.output_text.pack(fill="both", expand=True)
        tk.Button(self, text="Copy to Clipboard", command=self.copy_output).pack(fill="x")
        tk.Button(self, text="Save to File", command=self.save_output).pack(fill="x")

    def load_modules(self):
        modules = []
        for fname in os.listdir(MODULE_DIR):
            if fname.endswith(".py") and not fname.startswith(("_", "base")):
                module_name = f"document_builders.form_modules.{fname[:-3]}"
                mod = importlib.import_module(module_name)
                modules.append(mod.Component)
        modules.sort(key=lambda c: c.name)
        return modules

    def add_component(self):
        selected_name = self.module_var.get()
        for comp_cls in self.available_modules:
            if comp_cls.name == selected_name:
                frame = tk.Frame(self.component_frame, bd=2, relief="groove", pady=2)
                comp = comp_cls(frame)
                comp.frame.pack(fill="x", expand=True)
                btn = tk.Button(frame, text="Remove", command=lambda f=frame, c=comp: self.remove_component(f, c))
                btn.pack(side="right")
                frame.pack(fill="x", pady=2)
                self.components.append((frame, comp))
                break

    def remove_component(self, frame, comp):
        frame.destroy()
        self.components = [p for p in self.components if p[1] is not comp]

    def generate_output(self):
        output = []
        for _, comp in self.components:
            text = comp.render().strip()
            if text:
                output.append(text)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n\n".join(output))

    def copy_output(self):
        text = self.output_text.get("1.0", tk.END)
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Copied", "Output copied to clipboard")

    def save_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if not text:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Saved to {path}")


def main() -> None:
    app = FormMaker()
    app.mainloop()


if __name__ == "__main__":
    main()
