# file_io/export.py

import json
import csv

def export_to_json(dictionary, file_path):
    """
    Export the dictionary to JSON format.

    Parameters:
    - dictionary: The dictionary to export.
    - file_path: The file path to save the exported dictionary to.

    Returns:
    - True if the export is successful, False otherwise.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(dictionary, file, indent=4)
        return True
    except Exception as e:
        print(f"An error occurred while exporting the dictionary to JSON: {e}")
        return False

def export_to_csv(dictionary, file_path):
    """
    Export the dictionary to CSV format.

    Parameters:
    - dictionary: The dictionary to export.
    - file_path: The file path to save the exported dictionary to.

    Returns:
    - True if the export is successful, False otherwise.
    """
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            for key, value in dictionary.items():
                writer.writerow([key, value])
        return True
    except Exception as e:
        print(f"An error occurred while exporting the dictionary to CSV: {e}")
        return False

def export_to_python(dictionary, file_path):
    """
    Export the dictionary to Python-compatible format.

    Parameters:
    - dictionary: The dictionary to export.
    - file_path: The file path to save the exported dictionary to.

    Returns:
    - True if the export is successful, False otherwise.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(f"dictionary = {str(dictionary)}")
        return True
    except Exception as e:
        print(f"An error occurred while exporting the dictionary to Python: {e}")
        return False

def export_to_plain_text(dictionary, file_path):
    """
    Export the dictionary to plain text format.

    Parameters:
    - dictionary: The dictionary to export.
    - file_path: The file path to save the exported dictionary to.

    Returns:
    - True if the export is successful, False otherwise.
    """
    try:
        with open(file_path, 'w') as file:
            for key, value in dictionary.items():
                file.write(f"{key}: {value}\n")
        return True
    except Exception as e:
        print(f"An error occurred while exporting the dictionary to plain text: {e}")
        return False

def export_to_clipboard(dictionary):
    """
    Export the dictionary to the clipboard as a Python-compatible representation.

    Parameters:
    - dictionary: The dictionary to export.

    Returns:
    - True if the export is successful, False otherwise.
    """
    try:
        import pyperclip
        pyperclip.copy(str(dictionary))
        return True
    except ImportError:
        print("Pyperclip module is not installed. Install it using 'pip install pyperclip'.")
        return False
    except Exception as e:
        print(f"An error occurred while exporting the dictionary to clipboard: {e}")
        return False