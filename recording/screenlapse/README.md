screencap_timelapse_tool/
├── gui/
│   ├── __init__.py
│   ├── main_gui.py  # Depends on: image_capture.py, timelapse_generation.py, customization_options.py, error_handling.py
│   └── helper_functions.py
├── image_capture/
│   ├── __init__.py
│   ├── screenshot.py
│   ├── program_capture.py
│   └── active_program_capture.py
├── timelapse_generation/
│   ├── __init__.py
│   ├── generate_timelapse.py  # Depends on: image_capture.py
│   ├── combine_images.py
│   └── add_effects.py
├── customization_options/
│   ├── __init__.py
│   ├── settings.py
│   ├── transitions.py
│   └── output.py
├── error_handling/
│   ├── __init__.py
│   └── error_handler.py
├── documentation/
│   └── user_guide.pdf
└── README.md

from gui.main_gui import create_gui, update_capture_frequency, update_source_options
from image_capture import capture_screen, save_screenshot
from timelapse_generation import combine_images, generate_timelapse
from customization_options import set_timelapse_duration, set_output_filename
from error_handling import handle_error
from documentation import show_documentation

def main():
    try:
        # Create GUI
        create_gui()
        
        # Update capture frequency based on user selection
        update_capture_frequency()
        
        # Update source options based on user selection
        update_source_options()
        
        # Capture screen or program
        captured_image = capture_screen()
        
        # Save screenshot
        save_screenshot(captured_image)
        
        # Combine captured screenshots
        combined_images = combine_images()
        
        # Generate timelapse video
        generate_timelapse(combined_images)
        
        # Set timelapse duration
        set_timelapse_duration()
        
        # Set output filename
        set_output_filename()
        
        # Show documentation
        show_documentation()
        
    except Exception as e:
        # Handle error and display error message
        handle_error(e)

if __name__ == "__main__":
    main()