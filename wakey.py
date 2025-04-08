"""
Voice Assistant with Continuous Listening
"""

import numpy as np
import sounddevice as sd
import os
from dotenv import load_dotenv

load_dotenv()

class VoiceAssistant:
    def __init__(self):
        """Initialize with medium Whisper model"""
        from audio.recorder import AudioRecorder
        from audio.transcriber import Transcriber
        from audio.synthesizer import VoiceSynthesizer
        from gemini_client import GeminiClient

        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(model_size="medium.en")
        self.synthesizer = VoiceSynthesizer()
        self.gemini = GeminiClient()

        import pvporcupine
        self.porcupine = pvporcupine.create(
            access_key=os.getenv("PORCUPINE_KEY"),
            keyword_paths=[os.getenv("WAKE_WORD_PATH")],
            sensitivities=[0.7]
        )
        self.is_active = False

    def run(self):
        """Main loop that never stops listening"""
        with sd.InputStream(
            samplerate=self.porcupine.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.porcupine.frame_length,
            callback=self._audio_callback
        ):
            print("🔊 Ready - Waiting for wake word...")
            try:
                while True:
                    sd.sleep(100)
            except KeyboardInterrupt:
                pass
            finally:
                self.porcupine.delete()

    def _audio_callback(self, indata, frames, time, status):
        """Immediate wake word handling"""
        if not self.is_active and self.porcupine.process(np.frombuffer(indata, dtype=np.int16)) >= 0:
            sd.stop()
            self._process_command()
            # Immediately resume listening without delay
            sd.sleep(100)

    def _process_command(self):
        """Process command with text feedback only"""
        try:
            self.is_active = True
            print("\n💬 Wake word detected - Recording...", end='', flush=True)

            audio = self.recorder.record_until_silence(
                max_seconds=10,
                silence_threshold=0.025,
                silence_duration=1.2
            )
            print("done")

            print("🔄 Transcribing...", end=' ', flush=True)
            text = self.transcriber.transcribe(audio)
            print(f"done\n🗣 You said: {text}")

            print("🧠 Generating response...", end=' ', flush=True)
            response = self.gemini.get_response(text)
            print(f"done\n🤖 Response: {response}")

            try:
                self.synthesizer.speak(response)
            except Exception as e:
                print(f"⚠ Couldn't speak response: {str(e)}")

        except Exception as e:
            print(f"\n⚠ Error: {str(e)}")
        finally:
            self.is_active = False
            print("\n🔊 Ready - Waiting for wake word...")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()