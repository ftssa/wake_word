"""
Central configuration for the voice assistant project.
All settings are loaded from environment variables with fallback defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration settings with the following hierarchy:
    1. Environment variables (.env file)
    2. Hardcoded defaults (when no env var exists)
    """

    # ========== WAKE WORD CONFIGURATION ==========
    WAKE_WORD = os.getenv("WAKE_WORD", "emily")  # Wake word phrase
    WAKE_WORD_NAME = "Emily"  # Display name
    WAKE_WORD_SENSITIVITY = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.7"))  # 0-1
    WAKE_WORD_PATH = os.path.normpath(os.getenv("WAKE_WORD_PATH"))  # Normalized path
    PORCUPINE_KEY = os.getenv("PORCUPINE_KEY")  # Picovoice access key

    # ========== AUDIO PROCESSING ==========
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))  # Hz
    FRAME_LENGTH = int(os.getenv("FRAME_LENGTH", "512"))  # Samples
    AUDIO_DIR = os.path.normpath(os.getenv("AUDIO_DIR", "audio_output"))  # Output directory
    USE_CUDA = False  # Set True if you have NVIDIA GPU

    # ========== ELEVENLABS TTS ==========
    ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Charlotte")
    ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

    # ========== GEMINI AI ==========
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

    @classmethod
    def validate(cls):
        """
        Validate critical configurations.
        Raises:
            ValueError: If required settings are missing
            FileNotFoundError: If key files don't exist
        """
        # Required API keys
        if not cls.PORCUPINE_KEY:
            raise ValueError("Missing PORCUPINE_KEY in .env file")
        if not cls.ELEVENLABS_KEY:
            raise ValueError("Missing ELEVENLABS_API_KEY in .env file")
        if not cls.GEMINI_KEY:
            raise ValueError("Missing GEMINI_API_KEY in .env file")

        # File paths
        if not os.path.exists(cls.WAKE_WORD_PATH):
            raise FileNotFoundError(f"Wake word model not found at: {cls.WAKE_WORD_PATH}")

        # Directory creation
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)

        # Value ranges
        if not 0 <= cls.WAKE_WORD_SENSITIVITY <= 1:
            raise ValueError("WAKE_WORD_SENSITIVITY must be between 0 and 1")