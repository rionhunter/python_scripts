# audio_feedback.py

import pyttsx3

class AudioFeedback:
    def __init__(self):
        self.engine = pyttsx3.init()

    def play_audio(self, audio_file):
        """
        Play audio feedback for successful import and any errors encountered during the process.
        
        Args:
            audio_file (str): The path or filename of the audio file to be played.
        """
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.8)
        self.engine.say(audio_file)
        self.engine.runAndWait()