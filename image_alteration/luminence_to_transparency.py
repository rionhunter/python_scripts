import tkinter as tk
from tkinter import filedialog
from PIL import Image

def calculate_luminosity(pixel):
    return int(0.21 * pixel[0] + 0.72 * pixel[1] + 0.07 * pixel[2])

def adjust_pixel(pixel):
    luminosity = calculate_luminosity(pixel)
    # Skewing RGB values
    if luminosity >= 243:  # 95% of 255
        return (255, 255, 255, 255)
    elif luminosity <= 12:  # 5% of 255
        return (0, 0, 0, 0)
    else:
        # Apply luminosity as transparency
        return (pixel[0], pixel[1], pixel[2], luminosity)

def process_images(file_paths):
    for file_path in file_paths:
        image = Image.open(file_path).convert("RGBA")
        pixels = list(image.getdata())

        new_pixels = [adjust_pixel(pixel) for pixel in pixels]
        new_image = Image.new("RGBA", image.size)
        new_image.putdata(new_pixels)

        save_path = file_path.rsplit('.', 1)[0] + "_luminance_keyed.png"
        new_image.save(save_path)
        print(f"Processed and saved: {save_path}")

def select_images():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    root.destroy()

    if file_paths:
        process_images(file_paths)

if __name__ == "__main__":
    select_images()
