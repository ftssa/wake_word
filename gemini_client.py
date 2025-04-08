"""
Google Gemini API client with error handling and conversation management.
Handles all communication with Gemini's generative AI models.
"""

import google.generativeai as genai
from config import Config
from typing import Generator
import logging

import google.generativeai as genai
from config import Config
import logging


class GeminiClient:
    def __init__(self):
        try:
            if not Config.GEMINI_KEY:
                raise ValueError("Gemini API key not configured")

            genai.configure(api_key=Config.GEMINI_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Updated model name
            logging.info("Gemini client initialized")
        except Exception as e:
            logging.error(f"Gemini init failed: {str(e)}")
            raise

    def get_response(self, prompt: str):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Gemini error: {str(e)}")
            return "Sorry, I couldn't process that request."


    def reset_conversation(self):
        """Clear current conversation history."""
        self.conversation = None
        logging.info("Conversation reset")