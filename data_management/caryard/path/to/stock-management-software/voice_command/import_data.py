# import_data.py

import os
from datetime import datetime
from database.models import StockItem
from audio_feedback import speak

def import_data(file_path):
    """Import stock data from a csv file into the database."""
    if not os.path.isfile(file_path):
        speak("Error: File not found.")
        return

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # Remove header line
            header = lines[0]
            lines = lines[1:]

            for line in lines:
                # Split line into fields
                fields = line.strip().split(',')

                # Create a new stock item
                stock_item = StockItem()
                stock_item.name = fields[0]
                stock_item.description = fields[1]
                stock_item.price = float(fields[2])
                stock_item.quantity = int(fields[3])
                stock_item.date_added = datetime.now()

                # Save the stock item to the database
                stock_item.save()

        speak("Stock data imported successfully.")
    except Exception as e:
        speak(f"Error: {e}")