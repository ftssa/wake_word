import pvporcupine
import sounddevice as sd
import numpy as np
from config import Config


class VoiceRecorder:
    def __init__(self):
        Config.validate()
        self.porcupine = pvporcupine.create(
            access_key=Config.PORCUPINE_KEY,
            keyword_paths=[Config.WAKE_WORD_PATH],
            sensitivities=[0.7]
        )
        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length
        self.silence_threshold = 0.02  # 2% of max volume
        self.silence_limit = 1.5  # seconds
        self.recording = False
        self.silent_frames = 0
        self.frames = []

    def process_audio(self, audio_frame):
        """Process audio with proper type conversion"""
        # Convert to Porcupine-compatible format
        pcm = np.frombuffer(audio_frame, dtype=np.int16)

        if not self.recording:
            # Wake word detection
            if self.porcupine.process(pcm) >= 0:
                print("\n🔔 WAKE WORD DETECTED - Recording started...")
                self.recording = True
                self.frames = [pcm]
            return

        # Silence detection
        volume = np.abs(pcm).mean() / 32768
        if volume < self.silence_threshold:
            self.silent_frames += 1
            if self.silent_frames > int(self.silence_limit * self.sample_rate / self.frame_length):
                print("\n🔇 Silence detected - Recording stopped")
                self.save_recording()
                self.recording = False
                self.silent_frames = 0
        else:
            self.silent_frames = 0
            self.frames.append(pcm)

    def save_recording(self):
        """Save recorded audio"""
        if len(self.frames) > 0:
            audio = np.concatenate(self.frames)
            print(f"💾 Recorded {len(audio) / self.sample_rate:.2f} seconds")
            # Add your save/processing logic here

    def listen(self):
        try:
            with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16',
                    blocksize=self.frame_length,
                    callback=self.audio_callback
            ):
                print(f"👂 Waiting for wake word ({Config.WAKE_WORD_NAME})...")
                while True:
                    sd.sleep(100)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        finally:
            self.porcupine.delete()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print("Audio status:", status)
        self.process_audio(indata.copy())


if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.listen()
