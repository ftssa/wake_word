# audio/transcriber.py
import torch
import numpy as np
from config import Config
import warnings


class Transcriber:
    def __init__(self, model_size: str = "base.en"):
        self.device = self._get_device()
        self.model = self._load_model(model_size)

    def _get_device(self):
        """Determine the best available device"""
        if Config.USE_CUDA and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _load_model(self, model_size):
        """Try multiple loading methods"""
        try:
            import whisper
            print(f"✅ Using Whisper ({model_size}) on {self.device.upper()}")
            return whisper.load_model(model_size, device=self.device)
        except Exception as e:
            warnings.warn(f"Whisper failed: {str(e)}")
            return None

    def transcribe(self, audio_np: np.ndarray) -> str:
        """Convert audio to text with robust validation"""
        if not isinstance(audio_np, np.ndarray) or audio_np.size == 0:
            return "[No audio detected]"

        try:
            # Convert and validate audio
            audio_float = self._prepare_audio(audio_np)
            if audio_float is None:
                return "[Invalid audio]"

            if self.model:
                result = self.model.transcribe(audio_float)
                return result["text"].strip()
            return self._fallback_transcribe(audio_float)

        except Exception as e:
            print(f"🔴 Transcription error: {str(e)}")
            return "[Transcription failed]"

    def _prepare_audio(self, audio_np):
        """Validate and normalize audio input"""
        try:
            audio_float = audio_np.astype(np.float32) / 32768.0
            if audio_float.size == 0 or np.isnan(audio_float).any():
                return None

            # Remove silent chunks
            audio_float = audio_float[np.abs(audio_float) > 0.001]
            if audio_float.size == 0:
                return None

            return audio_float
        except:
            return None

    def _fallback_transcribe(self, audio_float):
        """More reliable fallback method"""
        try:
            import speech_recognition as sr
            import soundfile as sf
            from io import BytesIO

            # Normalize volume
            audio_float = audio_float / np.max(np.abs(audio_float))

            with BytesIO() as f:
                sf.write(f, audio_float, Config.SAMPLE_RATE, format='WAV')
                f.seek(0)
                r = sr.Recognizer()
                with sr.AudioFile(f) as source:
                    audio = r.record(source)
                    return r.recognize_google(audio)
        except Exception as e:
            print(f"⚠️ Fallback failed: {str(e)}")
            return "[Could not transcribe audio]"