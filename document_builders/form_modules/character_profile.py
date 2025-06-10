import tkinter as tk
from .base import FormComponent

class Component(FormComponent):
    """Character profile component."""

    name = "Character Profile"

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        tk.Label(self.frame, text="Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self.frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(self.frame, text="Age:").grid(row=1, column=0, sticky="w")
        self.age_entry = tk.Entry(self.frame, width=10)
        self.age_entry.grid(row=1, column=1, sticky="w")

        tk.Label(self.frame, text="Description:").grid(row=2, column=0, sticky="nw")
        self.desc = tk.Text(self.frame, width=40, height=3)
        self.desc.grid(row=2, column=1, sticky="ew")

    def render(self) -> str:
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        desc = self.desc.get("1.0", tk.END).strip()
        lines = []
        if name:
            lines.append(f"Name: {name}")
        if age:
            lines.append(f"Age: {age}")
        if desc:
            lines.append(desc)
        return "\n".join(lines) + "\n"
