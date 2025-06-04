import logging

# Define the error handler function
def handle_error(exception):
    # Log the error message
    logging.error(f"An error occurred: {exception}")
    
    # Show a user-friendly error message or notification
    show_error_message(exception)

def show_error_message(exception):
    # Display a pop-up window or GUI notification with the error message
    # Add code here to display the error message to the user
    print(f"Error: {exception}")

# Add other error handling functions if needed, such as for specific exceptions or error scenarios