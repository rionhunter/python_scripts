# program_capture.py

import time
import pyautogui
from PIL import Image

def capture_screen():
    """
    Capture the screen and return the captured image.
    
    Returns:
        Image: The captured screen image.
    """
    screenshot = pyautogui.screenshot()
    return screenshot

def save_screenshot(image):
    """
    Save the captured image as a screenshot.
    
    Args:
        image (Image): The captured screen image.
    """
    timestamp = int(time.time())
    file_name = f"screenshot_{timestamp}.png"
    image.save(file_name)

if __name__ == "__main__":
    # Capture screen
    captured_image = capture_screen()
    
    # Save screenshot
    save_screenshot(captured_image)

# Changes Made:
# - Removed type annotations in function signatures to ensure compatibility with older versions of Python.
# - Changed the return type annotation from "PIL.Image.Image" to "Image" for better readability.
# - Fixed the import statement for the Image class from PIL module to be more explicit.
# - Added comments to describe the purpose of each function.
# - Cleaned up the code formatting to adhere to PEP 8 guidelines.