import tkinter as tk
from tkinter import messagebox

class EditSlotsWindow:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.window = tk.Toplevel()
        self.window.title("Edit Slots")
        
        self.selected_slot = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create a listbox to display the slots
        self.slot_listbox = tk.Listbox(self.window)
        self.slot_listbox.pack(side=tk.LEFT)
        self.slot_listbox.bind("<<ListboxSelect>>", self.on_slot_selected)
        
        # Create a frame to contain the slot details
        self.slot_details_frame = tk.Frame(self.window)
        self.slot_details_frame.pack(side=tk.LEFT, padx=10)
        
        # Create a label and entry for slot name
        self.slot_name_label = tk.Label(self.slot_details_frame, text="Slot Name:")
        self.slot_name_label.pack()
        
        self.slot_name_entry = tk.Entry(self.slot_details_frame)
        self.slot_name_entry.pack()
        
        # Create radio buttons for value type
        self.value_type_label = tk.Label(self.slot_details_frame, text="Value Type:")
        self.value_type_label.pack()
        
        self.selected_value_type = tk.StringVar()
        
        self.string_radio = tk.Radiobutton(self.slot_details_frame, text="String", variable=self.selected_value_type,
                                           value="String")
        self.string_radio.pack()
        
        self.integer_radio = tk.Radiobutton(self.slot_details_frame, text="Integer", variable=self.selected_value_type,
                                            value="Integer")
        self.integer_radio.pack()
        
        self.float_radio = tk.Radiobutton(self.slot_details_frame, text="Float", variable=self.selected_value_type,
                                          value="Float")
        self.float_radio.pack()
        
        self.boolean_radio = tk.Radiobutton(self.slot_details_frame, text="Boolean", variable=self.selected_value_type,
                                            value="Boolean")
        self.boolean_radio.pack()
        
        self.nested_dict_radio = tk.Radiobutton(self.slot_details_frame, text="Nested Dictionary",
                                                variable=self.selected_value_type, value="Nested Dictionary")
        self.nested_dict_radio.pack()
        
        # Create buttons for adding, updating, and deleting slots
        self.add_button = tk.Button(self.window, text="Add Slot", command=self.add_slot)
        self.add_button.pack(pady=10)
        
        self.update_button = tk.Button(self.window, text="Update Slot", command=self.update_slot)
        self.update_button.pack()
        
        self.delete_button = tk.Button(self.window, text="Delete Slot", command=self.delete_slot)
        self.delete_button.pack()
        
        # Initialize the slot listbox with existing slots
        self.refresh_slot_listbox()
    
    def refresh_slot_listbox(self):
        # Clear the listbox
        self.slot_listbox.delete(0, tk.END)
        
        # Add the slots to the listbox
        for slot in self.dictionary.get_slots():
            self.slot_listbox.insert(tk.END, slot.name)
        
        # Clear the slot details
        self.clear_slot_details()
    
    def clear_slot_details(self):
        self.slot_name_entry.delete(0, tk.END)
        self.selected_value_type.set(None)
    
    def on_slot_selected(self, event):
        # Get the selected slot from the listbox
        selected_index = self.slot_listbox.curselection()
        
        if len(selected_index) > 0:
            selected_name = self.slot_listbox.get(selected_index[0])
            self.selected_slot = self.dictionary.get_slot(selected_name)
            
            # Update the slot details
            self.slot_name_entry.delete(0, tk.END)
            self.slot_name_entry.insert(tk.END, self.selected_slot.name)
            
            self.selected_value_type.set(self.selected_slot.value_type)
        
    def add_slot(self):
        # Get the slot name and value type from the entry and radio buttons
        slot_name = self.slot_name_entry.get()
        value_type = self.selected_value_type.get()
        
        if slot_name and value_type:
            try:
                self.dictionary.add_slot(slot_name, value_type)
                self.refresh_slot_listbox()
                
                messagebox.showinfo("Success", "Slot added successfully!")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please enter both slot name and value type.")
    
    def update_slot(self):
        if self.selected_slot:
            # Get the new slot name and value type from the entry and radio buttons
            new_slot_name = self.slot_name_entry.get()
            new_value_type = self.selected_value_type.get()
            
            if new_slot_name and new_value_type:
                try:
                    self.dictionary.update_slot(self.selected_slot.name, new_slot_name, new_value_type)
                    self.refresh_slot_listbox()
                    
                    messagebox.showinfo("Success", "Slot updated successfully!")
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showwarning("Warning", "Please enter both new slot name and value type.")
        else:
            messagebox.showwarning("Warning", "Please select a slot from the list.")
    
    def delete_slot(self):
        if self.selected_slot:
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this slot?")
            
            if confirm:
                self.dictionary.delete_slot(self.selected_slot.name)
                self.refresh_slot_listbox()
                
                messagebox.showinfo("Success", "Slot deleted successfully!")
        else:
            messagebox.showwarning("Warning", "Please select a slot from the list.")
