# gui/window.py

import tkinter as tk
from tkinter import messagebox
import create_dictionary_window
import add_slots_window
import edit_slots_window
import duplicate_dict_window

class ApplicationWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dictionary Constructor")
        
        self.current_window = None
        
    def start(self):
        self.root.mainloop()
        
    def navigate_to_create_dictionary_window(self):
        if self.current_window:
            self.current_window.destroy()  # Destroy the current window if exists
            
        self.current_window = create_dictionary_window.CreateDictionaryWindow(self.root)
        self.current_window.pack()
        
    def navigate_to_add_slots_window(self):
        if self.current_window:
            self.current_window.destroy()  # Destroy the current window if exists
            
        self.current_window = add_slots_window.AddSlotsWindow(self.root)
        self.current_window.pack()
        
    def navigate_to_edit_slots_window(self):
        if self.current_window:
            self.current_window.destroy()  # Destroy the current window if exists
            
        self.current_window = edit_slots_window.EditSlotsWindow(self.root)
        self.current_window.pack()
        
    def navigate_to_duplicate_dict_window(self):
        if self.current_window:
            self.current_window.destroy()  # Destroy the current window if exists
            
        self.current_window = duplicate_dict_window.DuplicateDictWindow(self.root)
        self.current_window.pack()