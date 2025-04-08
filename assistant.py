import threading
import time
from queue import Queue
from gemini_client import GeminiClient
import audio.synthesizer


# Assuming your wake word detector uses similar interface
class WakeWordDetector:
    def __init__(self):
        self.model_path = model_path
        self.wake_word = wake_word
        self.callback = callback
        self.running = False

    def start(self):
        """Start listening for wake word in background"""
        self.running = True
        print(f"🔊 Listening for wake word: '{self.wake_word}'...")
        # Add your actual wake word detection implementation here
        # This is just a simulation thread
        self.thread = threading.Thread(target=self._detect_loop)
        self.thread.start()

    def _detect_loop(self):
        """Simulated detection loop - replace with actual audio processing"""
        while self.running:
            time.sleep(5)  # Replace with actual detection
            self.callback()  # Simulate wake word detection
            break  # Remove this in actual implementation


class VoiceAssistant:
    def __init__(self):
        self.gemini = GeminiClient()
        self.synthesizer = audio.VoiceSynthesizer()

        # Initialize wake detector with YOUR model path
        self.wake_detector = WakeWordDetector(
            model_path='models/wakey.tflite',  # Update with your actual model path
            wake_word=Config.WAKE_WORD.lower(),
            callback=self.on_wake_detected
        )

        self.is_active = False
        self.audio_queue = Queue()
        self.audio_thread = threading.Thread(target=self._audio_worker)

    def on_wake_detected(self):
        """Handle wake word detection"""
        if not self.is_active:
            print(f"\n⭐ Wake word '{Config.WAKE_WORD}' detected!")
            self.is_active = True
            self._process_conversation()

    def _process_conversation(self):
        """Handle full voice interaction cycle"""
        try:
            # 1. Capture user input
            user_query = self._capture_voice_input()

            if not user_query:
                print("No speech detected")
                return

            # 2. Process with Gemini
            response = self.gemini.get_response(user_query)

            # 3. Stream response
            full_response = []
            for chunk in response:
                full_response.append(chunk)
                self.audio_queue.put(chunk)  # Queue for audio playback

            # 4. Save conversation
            self.synthesizer.speak(" ".join(full_response), save_audio=True)

        except Exception as e:
            print(f"Error in conversation: {e}")
        finally:
            self.is_active = False

    def _capture_voice_input(self) -> str:
        """Implement your actual speech-to-text here"""
        print("🎤 Listening for query...")
        time.sleep(1)  # Simulate listening
        return "Tell me about yourself"  # Replace with actual STT

    def _audio_worker(self):
        """Dedicated thread for audio playback"""
        while True:
            text = self.audio_queue.get()
            if text is None:  # Exit signal
                break
            try:
                self.synthesizer.speak(text, save_audio=False)
            except Exception as e:
                print(f"Audio playback error: {e}")

    def start(self):
        """Launch the assistant"""
        self.audio_thread.start()
        self.wake_detector.start()
        print("🚀 Assistant started")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Cleanup resources"""
        print("\n🛑 Shutting down...")
        self.wake_detector.running = False
        self.audio_queue.put(None)
        self.audio_thread.join()


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start()