import subprocess


def capture_active_program():
    """
    Captures the active program window and returns the captured image.
    """
    try:
        # Use subprocess to execute the command to capture the active program window
        subprocess.run(["screencapture", "-x", "-C", "active_program.png"], check=True)
        
        # Read the captured image file
        with open("active_program.png", "rb") as f:
            captured_image = f.read()
        
        return captured_image
    
    except subprocess.CalledProcessError as e:
        # Raise exception if an error occurs during the capture process
        raise Exception("Error capturing the active program window: {}".format(str(e)))