import tkinter as tk

class FormComponent:
    """Base class for form components."""

    name = "Base"

    def __init__(self, master: tk.Misc):
        self.frame = tk.Frame(master)

    def render(self) -> str:
        """Return the text output for this component."""
        return ""
