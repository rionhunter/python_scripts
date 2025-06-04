from chatgpt.chatgpt_interface import ChatGptInstance
from chatgpt.whisper_api import WhisperAPI

class ChatGptApi:
    def __init__(self):
        self.chatGptInstance = ChatGptInstance()
        self.whisperAPI = WhisperAPI()

    def chat(self, message):
        """Interact with ChatGPT to process user input and generate response."""
        response = self.chatGptInstance.generate_response(message)
        return response

    def whisper(self, message):
        """Use Whisper API to enhance the natural language capabilities of ChatGPT."""
        response = self.whisperAPI.enhance_language(message)
        return response

# Unit tests or additional code for testing and debugging can be added below this point.