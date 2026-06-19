import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import sys
from PyQt6.QtWidgets import QApplication
# Ensure project root on path for local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from gui.main_window import MainWindow

print('Starting')
app = QApplication(sys.argv[:1])
print('QApplication created')
win = MainWindow()
print('MainWindow constructed')
win.close()
print('Done')
