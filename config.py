# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Direct attribute access (no @property)
    PORCUPINE_KEY = os.getenv("PORCUPINE_KEY")
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    WAKE_WORD_NAME = "Emily"  # Display name
    # Audio Settings
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
    FRAME_LENGTH = int(os.getenv("FRAME_LENGTH", "512"))
    # Audio
    SAMPLE_RATE = 16000
    FRAME_LENGTH = 512
    USE_CUDA = False  # Set True if you have NVIDIA GPU


    # Paths (Windows)
    WAKE_WORD_PATH = os.getenv("WAKE_WORD_PATH").replace('\\', '/')  # Normalize path

    @classmethod
    def validate(cls):
        """Check required configurations"""
        if not cls.PORCUPINE_KEY:
            raise ValueError("Missing Porcupine key in .env file")
        if not os.path.exists(cls.WAKE_WORD_PATH):
            raise FileNotFoundError(f"Wake word file not found at: {cls.WAKE_WORD_PATH}")