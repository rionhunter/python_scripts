# generate_timelapse.py

from image_capture import capture_screen
from timelapse_generation import combine_images, generate_timelapse
from customization_options import set_timelapse_duration, set_output_filename
from error_handling import handle_error
from documentation import show_documentation

def generate_timelapse_script():
    try:
        # Capture screen or program
        captured_image = capture_screen()
        
        # Combine captured screenshots
        combined_images = combine_images(captured_image)
        
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