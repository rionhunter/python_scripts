import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import QRect, Qt

class ImageCropper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Cropper Supreme')
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)
        self.label.resize(800, 550)

        btnOpen = QPushButton('Open Image', self)
        btnOpen.move(10, 560)
        btnOpen.clicked.connect(self.openImage)

        btnSave = QPushButton('Save Image', self)
        btnSave.move(110, 560)
        btnSave.clicked.connect(self.saveImage)

        self.startPoint = self.endPoint = None
        self.show()

    def openImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Images (*.png *.xpm *.jpg)')
        if filePath:
            self.imagePath = filePath
            self.pixmap = QPixmap(filePath)
            self.scaledPixmap()
            self.update()

    def scaledPixmap(self):
        screenWidth = self.label.width()
        screenHeight = self.label.height()
        if self.pixmap.width() > screenWidth * 0.8 or self.pixmap.height() > screenHeight * 0.8:
            self.pixmap = self.pixmap.scaled(int(screenWidth * 0.8), int(screenHeight * 0.8), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)


    def paintEvent(self, event):
        super().paintEvent(event)
        if self.startPoint and self.endPoint:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(QRect(self.startPoint, self.endPoint))
            darkMask = QColor(0, 0, 0, 100)
            painter.fillRect(self.rect(), darkMask)
            painter.fillRect(QRect(self.startPoint, self.endPoint), QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode_Overlay)

    def mousePressEvent(self, event):
        self.startPoint = event.pos()
        self.endPoint = None
        self.update()

    def mouseMoveEvent(self, event):
        self.endPoint = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.endPoint = event.pos()
        self.update()

    def saveImage(self):
        if self.startPoint and self.endPoint:
            rect = QRect(self.startPoint, self.endPoint)
            croppedImage = self.pixmap.copy(rect)
            croppedImagePath = self.imagePath.rsplit('.', 1)[0] + '_cropped.' + self.imagePath.split('.')[-1]
            croppedImage.save(croppedImagePath)
            print(f"Image saved as: {croppedImagePath}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageCropper()
    sys.exit(app.exec_())
