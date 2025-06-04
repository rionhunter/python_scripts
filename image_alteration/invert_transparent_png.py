from PIL import Image
import tkinter as tk
from tkinter import filedialog


def invert_png_transparency(file_path, output_path):
    # Open the image
    img = Image.open(file_path).convert("RGBA")
    r, g, b, a = img.split()

    # Create an empty list to store inverted pixel data
    inverted_data = []

    # Get the pixel data
    pixels = img.getdata()

    for pixel in pixels:
        red, green, blue, alpha = pixel
        # Only invert if alpha is above the threshold (20% opaque or more)
        if alpha > 51:  # 51 out of 255 is approximately 20%
            inverted_data.append((255 - red, 255 - green, 255 - blue, alpha))
        else:
            # Leave it unchanged if mostly transparent
            inverted_data.append((red, green, blue, alpha))

    # Create a new image with inverted data
    inverted_img = Image.new("RGBA", img.size)
    inverted_img.putdata(inverted_data)

    # Save the output image
    inverted_img.save(output_path, "PNG")


def select_image_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Open file dialog to select an image
    file_path = filedialog.askopenfilename(title="Select an image file", filetypes=[("PNG files", "*.png")])
    if not file_path:
        print("No file selected. Exiting.")
        return

    # Set output file path
    output_path = filedialog.asksaveasfilename(title="Save inverted image as", defaultextension=".png",
                                               filetypes=[("PNG files", "*.png")])
    if not output_path:
        print("No output file selected. Exiting.")
        return

    # Invert the selected image
    invert_png_transparency(file_path, output_path)
    print(f"Inverted image saved to: {output_path}")


if __name__ == "__main__":
    select_image_file()
