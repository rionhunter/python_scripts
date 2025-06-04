import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog, QSlider, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import io

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_color = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Background Remover')

        layout = QVBoxLayout(self)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.open_button = QPushButton('Open Image', self)
        self.open_button.clicked.connect(self.openImage)
        layout.addWidget(self.open_button)

        self.color_button = QPushButton('Pick Background Color', self)
        self.color_button.clicked.connect(self.pickColor)
        layout.addWidget(self.color_button)

        self.fuzziness_label = QLabel('Fuzziness: 0', self)
        layout.addWidget(self.fuzziness_label)

        self.fuzziness_slider = QSlider(Qt.Horizontal, self)
        self.fuzziness_slider.setMinimum(0)
        self.fuzziness_slider.setMaximum(255)
        self.fuzziness_slider.valueChanged.connect(self.updateFuzziness)
        layout.addWidget(self.fuzziness_slider)

        self.preview_label = QLabel(self)
        layout.addWidget(self.preview_label)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.valueChanged.connect(self.updatePreview)
        layout.addWidget(self.slider)

        self.save_button = QPushButton('Save Images', self)
        self.save_button.clicked.connect(self.saveImages)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def openImage(self):
        options = QFileDialog.Options()
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)", options=options)
        if self.file_name:
            self.loadImage(self.file_name)
            print(f"Image loaded: {self.file_name}")

    def loadImage(self, path):
        try:
            self.original_image = Image.open(path)
            self.updatePreview()
        except Exception as e:
            logging.error(e)
            print(e)

    def pickColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color
            self.updatePreview()
            print(f"Selected color: {self.selected_color.name()}")

    def updateFuzziness(self):
        self.fuzziness_label.setText(f'Fuzziness: {self.fuzziness_slider.value()}')
        self.updatePreview()

    def updatePreview(self):
        if hasattr(self, 'original_image') and self.selected_color:
            img = self.processImage(self.original_image.copy())
            self.displayImage(img)

    def processImage(self, img):
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if self.is_close(item[0:3], self.selected_color.getRgb()[:3], self.fuzziness_slider.value()):
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        return img

    def is_close(self, color1, color2, fuzziness):
        return all(abs(c1 - c2) <= fuzziness for c1, c2 in zip(color1, color2))

    def displayImage(self, img):
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue(), "PNG")
        self.image_label.setPixmap(pixmap.scaled(700, 700, Qt.KeepAspectRatio))

        # Update the slider
        self.slider.setMaximum(img.size[0] - 1)

    def saveImages(self):
        if hasattr(self, 'original_image') and self.selected_color:
            img = self.processImage(self.original_image.copy())
            for i in range(img.size[0]):
                new_image = img.crop((i, 0, i + 1, img.size[1]))
                new_image.save(f"{i}.png")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessor()
    ex.show()
    sys.exit(app.exec_())

