import tkinter as tk
from tkinter import messagebox
from dictionary.dictionary import Dictionary
from file_io.save_load import save_dictionary
from file_io.export import export_dictionary

class DuplicateDictWindow(tk.Toplevel):
    def __init__(self, parent, dictionaries):
        super().__init__(parent)
        self.parent = parent
        self.title("Duplicate Dictionary")
        self.dictionaries = dictionaries
        
        # Create and position GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Dictionary selection label
        dict_label = tk.Label(self, text="Select a dictionary to duplicate:")
        dict_label.pack()

        # Dictionary selection combobox
        self.dict_combobox = tk.ttk.Combobox(self, values=self.dictionaries)
        self.dict_combobox.pack()

        # Duplicate button
        duplicate_button = tk.Button(self, text="Duplicate", command=self.duplicate_dictionary)
        duplicate_button.pack()

    def duplicate_dictionary(self):
        # Get the selected dictionary name
        selected_dict = self.dict_combobox.get()

        if selected_dict:
            # Check if the dictionary name already exists
            if selected_dict in self.dictionaries:
                messagebox.showerror("Error", "Duplicate name already exists. Please choose a different name.")
                return

            # Get the dictionary object to duplicate
            dict_to_duplicate = self.parent.get_dictionary(selected_dict)

            # Create a new dictionary object by duplicating the selected dictionary
            new_dict = dict_to_duplicate.duplicate()

            # Save the new dictionary to a file
            save_dictionary(new_dict, selected_dict)

            # Export the new dictionary in various formats
            export_dictionary(new_dict, selected_dict)

            # Show success message
            messagebox.showinfo("Success", f"Dictionary '{selected_dict}' duplicated successfully!")

            # Close the duplicate dictionary window
            self.destroy()
        else:
            messagebox.showerror("Error", "Please select a dictionary to duplicate.")
