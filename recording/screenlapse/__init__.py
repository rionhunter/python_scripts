"""
screencap_timelapse_tool/gui/__init__.py

This module is part of the screencap timelapse tool project.
It contains the initialization code for the GUI components.

"""

from .main_gui import create_gui, update_capture_frequency, update_source_options
from ..image_capture import capture_screen, save_screenshot
from ..timelapse_generation import combine_images, generate_timelapse
from ..customization_options import set_timelapse_duration, set_output_filename
from ..error_handling import handle_error
from ..documentation import show_documentation


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
"""