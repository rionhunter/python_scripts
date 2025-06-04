import tkinter as tk
from tkinter import ttk

class AddSlotsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Slots")
        
        self.parent = parent
        self.slot_name = ""
        self.value_type = tk.StringVar()
        
        self.initialize()
    
    def initialize(self):
        # Slot name label and entry
        slot_name_label = ttk.Label(self, text="Slot Name:")
        slot_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.slot_name_entry = ttk.Entry(self)
        self.slot_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Value type label and combobox
        value_type_label = ttk.Label(self, text="Value Type:")
        value_type_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.value_type_combobox = ttk.Combobox(self, textvariable=self.value_type)
        self.value_type_combobox["values"] = ["String", "Integer", "Float", "Boolean", "Nested Dictionary"]
        self.value_type_combobox.current(0)
        self.value_type_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Add slot button
        add_slot_button = ttk.Button(self, text="Add Slot", command=self.add_slot)
        add_slot_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        
    def add_slot(self):
        self.slot_name = self.slot_name_entry.get()
        self.parent.add_slot(self.slot_name, self.value_type.get())
        self.destroy()
