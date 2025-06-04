import pyautogui

def capture_screen():
    """
    Capture a screenshot of the entire screen.
    Return the captured image.
    """
    screenshot = pyautogui.screenshot()
    return screenshot

def get_program_window(window_name):
    """
    Get the window object for a specific program with the given window name.
    Return the window object if found, otherwise raise an exception.
    """
    # Code to get the program window using appropriate API/library
    # ...
    # If window not found, raise an exception
    raise Exception(f"Window '{window_name}' not found")

def capture_program_window(window_name):
    """
    Capture a screenshot of a specific program window with the given window name.
    Return the captured image.
    """
    program_window = get_program_window(window_name)
    screenshot = program_window.capture_screenshot()
    return screenshot

def capture_active_program():
    """
    Capture a screenshot of the active program window.
    Return the captured image.
    """
    active_program_window = get_active_program_window()
    screenshot = active_program_window.capture_screenshot()
    return screenshot