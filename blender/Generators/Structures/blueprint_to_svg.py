import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageDraw, ImageTk
import os


class App:
    def __init__(self, master):
        self.master = master
        master.title("Blueprint to SVG Converter")

        # Set up the canvas for displaying the image
        self.canvas = tk.Canvas(master, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.pick_color)  # Bind the left mouse button click to pick_color

        # Set up the buttons for selecting an image and a line thickness
        self.image_button = tk.Button(master, text="Select Image", command=self.select_image)
        self.image_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.color_button = tk.Button(master, text="Pick Color", command=self.pick_color_from_image)
        self.color_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.thickness_slider = tk.Scale(master, from_=0, to=10, orient=tk.HORIZONTAL, label="Line Thickness",
                                         command=self.tint_image)
        self.thickness_slider.pack(side=tk.LEFT, padx=10, pady=10)

        # Set the default line thickness and color
        self.thickness = 2
        self.color = None

    def select_image(self):
        # Set the initial directory to the current working directory
        initial_dir = os.getcwd()

        # Show a file dialog for selecting the image file
        self.filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")],
                                                   initialdir=initial_dir)

        if self.filename:
            # Load the image and display it in the canvas
            self.img = Image.open(self.filename)
            self.display_image()

    def display_image(self):
        # Display the image in the canvas, scaled to fit within the canvas
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_width, img_height = self.img.size

        if img_width > canvas_width or img_height > canvas_height:
            # Scale down the image to fit within the canvas
            aspect_ratio = img_width / img_height
            if aspect_ratio > 1:
                new_width = canvas_width
                new_height = int(canvas_width / aspect_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * aspect_ratio)
            img = self.img.resize((new_width, new_height), resample=Image.LANCZOS)
        else:
            img = self.img

        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.delete('all')
        self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.img_tk)

    def pick_color_from_image(self):
        # Set the cursor to a crosshair and bind the left mouse button to pick_color
        self.canvas.config(cursor="crosshair")
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.pick_color)

    def pick_color(self, event):
        # Pick the color of the clicked pixel and update the color button
        x, y = event.x, event.y
        r, g, b = self.img.getpixel((x, y))
        self.color = (r, g, b)
        self.color_button.config(bg=self.rgb_to_hex(self.color))
        self.tint_image()

    def tint_image(self, event=None):
        if self.img and self.color:
            # Create a tinted copy of the image
            img_tinted = self.img.copy()
            draw = ImageDraw.Draw(img_tinted)

            # Convert the color to RGB format
            color_rgb = (self.color[0], self.color[1], self.color[2])

            # Loop over each pixel in the image and draw a line on it if the luminance is greater than the line thickness
            for y in range(img_tinted.size[1]):
                for x in range(img_tinted.size[0]):
                    # Get the pixel color and calculate its luminance
                    r, g, b = img_tinted.getpixel((x, y))
                    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b

                    # Only draw lines on pixels that are brighter than the selected luminance
                    if luma >= self.thickness * 10:
                        # Determine the color of the line based on the selected color and the pixel color
                        if self.color == "pick":
                            line_color = (r, g, b)  # Use the original color of the pixel
                        else:
                            line_color = color_rgb  # Use the selected color

                        # Draw a line on the pixel with the selected line thickness and color
                        draw.line([(x, y), (x+1, y)], fill=line_color, width=self.thickness)

            # Update the displayed image with the tinted image
            self.display_image()

    def rgb_to_hex(self, color):
        # Convert an RGB color tuple to a hexadecimal string
        r, g, b = color
        return f"#{r:02x}{g:02x}{b:02x}"

    def run(self):
        self.master.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.run()
       
