import numpy as np
import sounddevice as sd
from audio.recorder import AudioRecorder
from audio.transcriber import Transcriber  # Changed to match class name
from config import Config


class VoiceAssistant:
    def __init__(self):
        # Initialize components
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(model_size="base.en")  # Fixed initialization
        self.porcupine = self._init_wake_word()

    # ... rest of your code remains the same ...

    def _init_wake_word(self):
        """Initialize wake word detection"""
        try:
            import pvporcupine
            return pvporcupine.create(
                access_key=Config.PORCUPINE_KEY,
                keyword_paths=[Config.WAKE_WORD_PATH],
                sensitivities=[0.7]
            )
        except Exception as e:
            print(f"⚠️ Wake word disabled: {str(e)}")
            return None

    def process_command(self):
        """Full voice command processing"""
        print("\n🔵 Speak your command after the beep...")
        audio = self.recorder.record_until_silence(
            max_seconds=10,
            silence_threshold=0.02,
            silence_duration=1.5
        )

        print("\n🟠 Transcribing...")
        text = self.transcriber.transcribe(audio)
        print(f"\n💬 You said: {text}")
        return text

    def run(self):
        try:
            if not self.porcupine:
                print("🔴 Running in text-only mode (no wake word)")
                self.process_command()
                return

            print(f"\n👂 Listening for '{Config.WAKE_WORD_NAME}'... (Ctrl+C to exit)")
            with sd.InputStream(
                    samplerate=self.porcupine.sample_rate,
                    channels=1,
                    dtype='int16',
                    blocksize=self.porcupine.frame_length,
                    callback=self._audio_callback
            ):
                while True:
                    sd.sleep(100)

        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            if self.porcupine:
                self.porcupine.delete()

    def _audio_callback(self, indata, frames, time, status):
        """Handle wake word detection"""
        if status:
            print("Audio status:", status)

        if self.porcupine.process(np.frombuffer(indata, dtype=np.int16)) >= 0:
            sd.stop()  # Stop streaming temporarily
            self.process_command()
            print(f"\n👂 Listening for '{Config.WAKE_WORD_NAME}'...")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()