# voice_commands.py

import os
from import_data import import_data
from audio_feedback import audio_feedback

class VoiceCommands:
    def __init__(self, database):
        self.database = database

    def import_stock_listings(self, file_path):
        """Import the current stock listings into the database."""
        if os.path.exists(file_path):
            stock_listings = import_data(file_path)
            self.database.update_stock_listings(stock_listings)
            audio_feedback("Stock listings imported successfully.")
        else:
            audio_feedback("File not found.")

    def execute_voice_command(self, voice_command):
        """Execute the given voice command."""
        if "import" in voice_command:
            file_path = voice_command.split("import ")[-1]
            self.import_stock_listings(file_path)
        elif "retrieve" in voice_command:
            car_id = voice_command.split("retrieve ")[-1]
            car_location = self.database.get_car_location(car_id)
            if car_location:
                audio_feedback(f"The car is located at {car_location}.")
            else:
                audio_feedback("Car not found.")
        else:
            audio_feedback("Invalid voice command.")

    def start_listening(self):
        """Start listening for voice commands."""
        while True:
            voice_command = listen_for_voice_command()
            self.execute_voice_command(voice_command)