import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Menu Inception")

# Create a menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Create a dropdown menu
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)

# Add some items to the dropdown menu
file_menu.add_command(label="New")
file_menu.add_command(label="Open")

# Create a submenu
edit_menu = tk.Menu(file_menu, tearoff=0)
edit_menu.add_command(label="Undo")
edit_menu.add_command(label="Redo")

# Add the submenu to the dropdown menu
file_menu.add_cascade(label="Edit", menu=edit_menu)

# Run the main application window
root.mainloop()
