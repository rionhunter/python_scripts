import tkinter as tk

def copy_to_clipboard(event=None):
    text = entry.get()
    if text:  # Only copy text if there is something in the entry
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # Ensures clipboard content persists after the window closes
    root.destroy()  # Close the application

def refresh_focus():
    # Temporarily shift focus to another widget, then back to the entry
    dummy.focus_set()  # Focus on a dummy widget
    entry.focus_set()  # Refocus on the entry widget
    root.after(5000, refresh_focus)  # Adjust the timing as needed

# Create the main window
root = tk.Tk()
root.title("Text Entry to Clipboard")

# Create an entry widget
entry = tk.Entry(root, width=50)
entry.pack(pady=20)
entry.focus_set()  # Automatically focus the cursor on the entry field

# Create a dummy widget to shift focus
dummy = tk.Label(root, text="")
dummy.pack()

# Bind the Escape key to the copy_to_clipboard function
root.bind('<Escape>', copy_to_clipboard)

# Start the periodic refocus to ensure the entry updates
root.after(5000, refresh_focus)

# Start the GUI event loop
root.mainloop()
