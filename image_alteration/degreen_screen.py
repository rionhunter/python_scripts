import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

class GreenScreenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Green Screen Remover")

        # Image panel
        self.panel = tk.Label(root)
        self.panel.pack()

        # Select image button
        btn_select = tk.Button(root, text="Select Image", command=self.select_image)
        btn_select.pack()

        # Tolerance slider
        self.tolerance_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, label="Tolerance")
        self.tolerance_slider.set(100)
        self.tolerance_slider.pack()

        # Feathering slider
        self.feathering_slider = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, label="Feathering")
        self.feathering_slider.pack()

        # Green desaturation slider
        self.desaturation_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Green Desaturation")
        self.desaturation_slider.pack()

        # Hue adjustment slider
        self.hue_slider = tk.Scale(root, from_=-180, to=180, orient=tk.HORIZONTAL, label="Hue Adjustment")
        self.hue_slider.pack()

        # Update button
        btn_update = tk.Button(root, text="Update Preview", command=self.update_image)
        btn_update.pack()

        # Save button
        btn_save = tk.Button(root, text="Save Image", command=self.save_image)
        btn_save.pack()

        self.img = None
        self.img_path = None
        self.img_display = None
        self.preview_size = (800, 600)  # Preview size

    def select_image(self):
        self.img_path = filedialog.askopenfilename()
        if self.img_path:
            self.img = cv2.imread(self.img_path)
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            self.update_preview()

    def update_preview(self):
        if self.img is not None:
            img_resized = cv2.resize(self.img, self.preview_size)
            self.img_display = ImageTk.PhotoImage(Image.fromarray(img_resized))
            self.panel.configure(image=self.img_display)

    def update_image(self):
        if self.img is not None:
            img_processed = self.process_image(self.img)
            img_resized = cv2.resize(img_processed, self.preview_size)
            self.img_display = ImageTk.PhotoImage(Image.fromarray(img_resized))
            self.panel.configure(image=self.img_display)

    def process_image(self, img):
        tolerance = self.tolerance_slider.get()
        feathering = max(1, self.feathering_slider.get())
        feathering = feathering if feathering % 2 == 1 else feathering + 1
        desaturation = self.desaturation_slider.get()
        hue_shift = self.hue_slider.get()

        # Convert to HSV for processing
        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        # Greenscreen removal
        lower_green = np.array([60 - tolerance, 100, 50])
        upper_green = np.array([60 + tolerance, 255, 255])
        mask = cv2.inRange(img_hsv, lower_green, upper_green)
        mask_inv = cv2.bitwise_not(mask)
        mask_inv_blurred = cv2.GaussianBlur(mask_inv, (feathering, feathering), 0)

        # Apply desaturation and hue adjustment
        img_hsv[:, :, 1] = img_hsv[:, :, 1] * (1 - desaturation / 100.0)  # Desaturate
        adjusted_hue = (img_hsv[:, :, 0].astype(int) + hue_shift / 2) % 180
        img_hsv[:, :, 0] = adjusted_hue.astype(np.uint8)
        img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)

        # Apply the mask to the image for transparency
        img_rgba = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2RGBA)
        img_rgba[:, :, 3] = mask_inv_blurred

        return img_rgba


    def save_image(self):
        if self.img is not None:
            img_processed = self.process_image(self.img)
            filename = self.img_path.rsplit('.', 1)[0] + '_transparent.png'
            
            # Convert the processed image from RGBA to BGRA before saving (OpenCV uses BGR format)
            img_bgra = cv2.cvtColor(img_processed, cv2.COLOR_RGBA2BGRA)
            cv2.imwrite(filename, img_bgra)
            print(f"Image saved as {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GreenScreenApp(root)
    root.mainloop()
