# Customization Options Settings

# Capture Frequency (in seconds)
# Specify the frequency at which the tool captures screenshots. Default value is 5 seconds.
CAPTURE_FREQUENCY = 5

# Source Options
# Specify the source for capturing screenshots: program, screen, or active program. Default value is program.
SOURCE_OPTIONS = ["program", "screen", "active program"]
SELECTED_SOURCE = "program"

# Timelapse Duration (in seconds)
# Specify the duration of the timelapse video. Default value is 60 seconds.
TIMELAPSE_DURATION = 60

# Output Filename
# Specify the filename for the generated timelapse video. Default value is "timelapse.mp4".
OUTPUT_FILENAME = "timelapse.mp4"

# Transitions and Effects
# Enable or disable transitions and effects for the timelapse video. Default value is True.
ENABLE_TRANSITIONS = True

# Save Location
# Specify the save location for the generated timelapse video. Default value is the current directory.
SAVE_LOCATION = "./"

# Other Customization Options...
# Add other customization options as needed.

from customization_options import settings

def main():
    # Create GUI
    create_gui()
    
    # Update capture frequency based on user selection
    update_capture_frequency()
    
    # Update source options based on user selection
    update_source_options()
    
    try:
        # Capture screen or program
        captured_image = capture_screen()
        
        # Save screenshot
        save_screenshot(captured_image)
        
        # Combine captured screenshots
        combined_images = combine_images()
        
        # Generate timelapse video
        generate_timelapse(combined_images)
        
        # Set timelapse duration
        set_timelapse_duration(settings.TIMELAPSE_DURATION)
        
        # Set output filename
        set_output_filename(settings.OUTPUT_FILENAME)
        
        # Show documentation
        show_documentation()
        
    except Exception as e:
        # Log error and display error message
        log_error(e)
        handle_error(e)

if __name__ == "__main__":
    main()