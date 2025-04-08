from elevenlabs.client import ElevenLabs
from elevenlabs import play
from config import Config
import logging
import pyttsx3

class VoiceSynthesizer:
    def __init__(self):
        self.client = None
        self.engine = None
        
        try:
            # Initialize ElevenLabs if API key exists
            if Config.ELEVENLABS_KEY:
                self.client = ElevenLabs(api_key=Config.ELEVENLABS_KEY)
                logging.info("ElevenLabs initialized")
            
            # Initialize fallback engine
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            logging.info("Fallback TTS initialized")
            
        except Exception as e:
            logging.error(f"TTS init failed: {str(e)}")
            raise

    def speak(self, text: str):
        if not text.strip():
            return
            
        try:
            # Try ElevenLabs first
            if self.client:
                audio = self.client.generate(
                    text=text,
                    voice=Config.ELEVENLABS_VOICE,
                    model=Config.ELEVENLABS_MODEL
                )
                play(audio)
                return
        except Exception as e:
            logging.warning(f"ElevenLabs failed: {str(e)}")
        
        # Fallback to pyttsx3
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Fallback failed: {str(e)}")
            print(f"\n📢 {text}\n")