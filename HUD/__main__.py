import os
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog
import json


# Define constants and variables
SETTINGS_FILE = "base_directory.txt"
DEFAULT_DIR = "C:/your/script/directory"  # Replace with your actual directory
ICON_SIZE = 32
BACKGROUND_COLOR = "#000000"
ICON_COLOR_ACTIVE = "#FFFFFF"
ICON_COLOR_INACTIVE = "#808080"
EDIT_MODE_KEY = "<F1>"

class ScriptHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("+0+0")  # Fullscreen
        self.wm_attributes("-topmost", True)  # Stays on top

        # Black background
        self.configure(bg=BACKGROUND_COLOR)

        # Script data and customization
        self.scripts = []
        self.icons = {}
        self.base_dir = self._get_saved_base_dir() or DEFAULT_DIR
        self.current_dir = self.base_dir
        self.depth = 0  # Folder depth for back button
        self.edit_mode = False  # Edit mode for icon placement and size

        # Create menu and buttons
        self.create_menu()
        self.settings_button = tk.Button(text="Settings", command=self.open_settings)
        self.settings_button.pack(side="left", padx=5, pady=5)
        self.edit_mode_button = tk.Button(text="Edit", command=self.toggle_edit_mode)
        self.edit_mode_button.pack(side="left", padx=5, pady=5)

        # Initial icon loading and binding events
        self.create_icon_menu()
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind(EDIT_MODE_KEY, lambda event: self.toggle_edit_mode())

    def _get_saved_base_dir(self):
        """Retrieves the stored base directory path, if available."""
        if os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return f.read().strip()
        return None

    def _save_base_dir(self, new_dir):
        """Updates and saves the base directory path."""
        self.base_dir = new_dir
        self.current_dir = self.base_dir
        self.depth = 0
        with open(SETTINGS_FILE, "w") as f:
            f.write(new_dir)
        self.scripts = []
        self.icons = {}
        self.create_icon_menu()

    def open_settings(self):
        """Opens a settings panel for changing the base directory."""
        # ... Same as previous implementation ...

    def create_menu(self):
        menu = tk.Menu(self)

        # Add home option
        menu.add_command(label="Home", command=self.go_home)

        # Add icons menu
        menu.add_cascade(label="Icons", menu=self.create_icon_menu())

        self.main_menu = menu
        self.config(menu=menu)

    def create_icon_menu(self):
        icon_menu = tk.Menu(self)

        # Add options for folders and files
        for entry in os.listdir(self.current_dir):
            entry_path = os.path.join(self.current_dir, entry)
            if os.path.isdir(entry_path):
                icon_menu.add_command(label=entry, command=lambda folder=entry_path: self.enter_folder(folder))
            else:
                icon_menu.add_command(label=entry, command=lambda f=entry_path: self.run_script(f))

        # Add separator and folder icon option
        icon_menu.add_separator()
        icon_menu.add_command(label="Folder Icon", command=lambda: self.add_icon("folder.png"))

        return icon_menu


    def add_icon(self, icon_path):
        # Load image and resize
        image = Image.open(icon_path).resize((ICON_SIZE, ICON_SIZE))
        image_tk = ImageTk.PhotoImage(image)

        # Create button with icon and script name label
        button = tk.Button(image=image_tk, command=lambda script=os.path.join(self.current_dir, icon_path[:-4]): self.run_script(script))
        label = tk.Label(text=icon_path[:-4], bg=BACKGROUND_COLOR, fg=ICON_COLOR_INACTIVE)

        # Bind edit mode events
        if self.edit_mode:
            button.bind("<Button-1>", lambda event: self.start_drag(event, button))
            button.bind("<B1-Motion>", lambda event: self.drag_icon(event, button))
            label.bind("<MouseWheel>", lambda event: self.resize_icon(event, label))
            label.bind("<Button-3>", lambda event: self.change_icon(event, button, label))

        # Pack button and label
        button.pack(side="left", padx=5, pady=5)
        label.pack(side="left", padx=5, pady=5)

        # Store icon and button references
        self.icons[icon_path] = (image_tk, button, label)

    def toggle_edit_mode(self):
        """Switches edit mode on and off, affecting icon interactions."""
        self.edit_mode = not self.edit_mode
        self.edit_mode_button.configure(text="Edit" if self.edit_mode else "Done")

        # Update button bindings based on edit mode
        for _, (image_tk, button, label) in self.icons.items():
            if self.edit_mode:
                button.bind("<Button-1>", lambda event: self.start_drag(event, button))
                button.bind("<B1-Motion>", lambda event: self.drag_icon(event, button))
                label.bind("<MouseWheel>", lambda event: self.resize_icon(event, label))
                label.bind("<Button-3>", lambda event: self.change_icon(event, button, label))
            else:
                button.unbind("<Button-1>")
                button.unbind("<B1-Motion>")
                label.unbind("<MouseWheel>")
                label.unbind("<Button-3>")

    def start_drag(self, event, button):
        """Initiates dragging of an icon in edit mode."""
        self.drag_data = {"button": button, "x_offset": event.x, "y_offset": event.y}

    def drag_icon(self, event, button):
        """Updates the position of a dragged icon in edit mode."""
        if self.drag_data:
            button.place(relx=event.x - self.drag_data["x_offset"], rely=event.y - self.drag_data["y_offset"])

    def resize_icon(self, event, label):
        """Increases or decreases the size of an icon in edit mode based on scroll direction."""
        new_size = ICON_SIZE + event.delta // 10
        if new_size >= 16 and new_size <= 64:
            label.configure(image=self.icons[label["text"]][0].zoom(new_size / ICON_SIZE))

    def change_icon(self, event, button, label):
        """Allows selection of a new icon image file in edit mode."""
        new_icon_path = filedialog.askopenfilename(title="Select Icon", filetypes=[("PNG files", "*.png")])
        if new_icon_path:
            self.add_icon(new_icon_path)
            self.icons[label["text"]][1].destroy()  # Remove old button
            self.icons[label["text"]][2].pack_forget()  # Unpack old label
            self.icons.pop(label["text"])  # Remove old icon reference


    def _save_customizations(self):
        """Saves custom icon positions, sizes, and paths to a file."""
        # save to 'icon_customisation.json'
        path = os.path.join(self.base_dir, "icon_customisation.json")
        with open(path, "w") as f:
            json.dump(self.icons, f)
            
        
        

def _load_customizations(self):
    """Loads previously saved custom icon configurations."""
    with open("icon_customisation.json", "r") as f:
        self.icons = json.load(f)
        if not os.path.isfile(file_path):
            return


    def go_home(self):
        """Returns to the base directory and resets the folder depth."""
        self.current_dir = self.base_dir
        self.depth = 0
        self.create_icon_menu()

    def enter_folder(self, folder_path):
        """Enters a folder and updates the icon menu accordingly."""
        self.current_dir = folder_path
        self.depth += 1
        self.create_icon_menu()

    def run_script(self, script_path):
        """Runs a script by opening it in the default application."""
        os.startfile(script_path)




    def __init__(self):
        # ... existing init logic ...
        self._load_customizations()

    
if __name__ == "__main__":
    app = ScriptHUD()
    app._save_customizations()