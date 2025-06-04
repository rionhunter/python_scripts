import os
import datetime
from tkinter import Tk, filedialog, Frame, Label, Button, Entry, Scrollbar, Toplevel, VERTICAL, HORIZONTAL, Canvas
from tkinter.ttk import Treeview
from PIL import Image, ImageTk

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Island Separator")

        self.files = []
        self.previews = {}
        self.preview_entries = {}  # Initialize preview_entries here

        self.frame = Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.label = Label(self.frame, text="Selected PNG Files:")
        self.label.pack()

        self.tree = Treeview(self.frame, columns=("Filename", "Output Name"), show="headings", selectmode="extended")
        self.tree.heading("Filename", text="Filename")
        self.tree.heading("Output Name", text="Output Name")
        self.tree.pack(fill="both", expand=True)

        self.add_button = Button(self.frame, text="Add PNG Files", command=self.add_files)
        self.add_button.pack(side="left")

        self.remove_button = Button(self.frame, text="Remove Selected", command=self.remove_files)
        self.remove_button.pack(side="left")

        self.preview_button = Button(self.frame, text="Preview Selected", command=self.preview_files)
        self.preview_button.pack(side="right")

        self.process_button = Button(self.frame, text="Process Files", command=self.process_files)
        self.process_button.pack(side="right")

    def add_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select PNG files",
            filetypes=[("PNG files", "*.png")]
        )
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                self.tree.insert("", "end", values=(file_path, os.path.basename(file_path)))

    def remove_files(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            file_path = self.tree.item(item)["values"][0]
            self.files.remove(file_path)
            self.tree.delete(item)

    def preview_files(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        self.preview_window = Toplevel(self.root)
        self.preview_window.title("Preview and Rename Files")
        self.preview_window.geometry("800x600")

        preview_frame = Frame(self.preview_window)
        preview_frame.pack(fill="both", expand=True)

        canvas = Canvas(preview_frame)
        scrollbar_y = Scrollbar(preview_frame, orient=VERTICAL, command=canvas.yview)
        scrollbar_x = Scrollbar(preview_frame, orient=HORIZONTAL, command=canvas.xview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar_y.set)
        canvas.configure(xscrollcommand=scrollbar_x.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        self.preview_entries = {}

        for item in selected_items:
            file_path = self.tree.item(item)["values"][0]
            islands, image = self.split_image_into_islands(file_path)
            preview_images = self.generate_preview_images(islands, image)
            
            for idx, preview_image in enumerate(preview_images):
                image_tk = ImageTk.PhotoImage(preview_image)

                label = Label(scrollable_frame, image=image_tk)
                label.image = image_tk
                label.pack()

                entry = Entry(scrollable_frame)
                entry.insert(0, f"{os.path.basename(file_path).split('.')[0]}_island_{idx + 1}.png")
                entry.pack()

                self.preview_entries[(file_path, idx)] = entry

        confirm_button = Button(scrollable_frame, text="Confirm File Names", command=self.confirm_preview)
        confirm_button.pack()

    def confirm_preview(self):
        self.preview_window.destroy()

    def process_files(self):
        for (file_path, idx), entry in self.preview_entries.items():
            try:
                output_name = entry.get()
                output_folder = os.path.join(os.path.dirname(file_path), f"{os.path.basename(file_path).split('.')[0]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
                os.makedirs(output_folder, exist_ok=True)
                preview_image = self.previews[(file_path, idx)][0]
                preview_image.save(os.path.join(output_folder, output_name))
            except Exception as e:
                print(f"Error processing file {file_path} island {idx}: {e}")

        print("Processing complete.")

    def split_image_into_islands(self, image_path):
        image = Image.open(image_path).convert('RGBA')
        width, height = image.size
        pixels = image.load()

        visited = set()
        islands = []

        def flood_fill(x, y):
            to_fill = [(x, y)]
            island = []

            while to_fill:
                x, y = to_fill.pop()
                if (x, y) in visited:
                    continue
                visited.add((x, y))
                island.append((x, y))

                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                        if pixels[nx, ny][3] != 0:
                            to_fill.append((nx, ny))

            return island

        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] != 0 and (x, y) not in visited:
                    island = flood_fill(x, y)
                    islands.append(island)

        return islands, image

    def generate_preview_images(self, islands, image):
        preview_images = []

        for island in islands:
            new_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
            new_pixels = new_image.load()

            for x, y in island:
                new_pixels[x, y] = image.getpixel((x, y))

            bbox = new_image.getbbox()
            cropped_image = new_image.crop(bbox)
            preview_images.append(cropped_image)

        return preview_images

if __name__ == "__main__":
    root = Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
