import tkinter as tk
from .base import FormComponent

class Component(FormComponent):
    """Simple title and body text component."""

    name = "Basic Text"

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        tk.Label(self.frame, text="Title:").grid(row=0, column=0, sticky="w")
        self.title = tk.Entry(self.frame, width=40)
        self.title.grid(row=0, column=1, sticky="ew")

        tk.Label(self.frame, text="Body:").grid(row=1, column=0, sticky="nw")
        self.body = tk.Text(self.frame, width=40, height=4)
        self.body.grid(row=1, column=1, sticky="ew")

    def render(self) -> str:
        title = self.title.get().strip()
        body = self.body.get("1.0", tk.END).strip()
        parts = []
        if title:
            parts.append(title)
        if body:
            parts.append(body)
        return "\n".join(parts) + "\n"
