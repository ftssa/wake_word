# audio/recorder.py
import numpy as np
import sounddevice as sd
from config import Config


class AudioRecorder:
    def __init__(self):
        self.sample_rate = Config.SAMPLE_RATE
        self.frames = []
        self.overflow_count = 0

    def record_until_silence(self, max_seconds=10, silence_threshold=0.02, silence_duration=1.5):
        """Robust recording with overflow protection"""
        self.frames = []
        self.overflow_count = 0
        silent_frames = 0
        required_silent_frames = int(silence_duration * self.sample_rate / Config.FRAME_LENGTH)

        def callback(indata, frames, time, status):
            nonlocal silent_frames
            if status.input_overflow:
                self.overflow_count += 1

            volume = np.abs(indata).mean() / 32768
            if volume < silence_threshold:
                silent_frames += 1
            else:
                silent_frames = 0
                self.frames.append(indata.copy())

        print("● Recording...", end="", flush=True)
        with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                blocksize=Config.FRAME_LENGTH,
                callback=callback
        ):
            while len(self.frames) < (max_seconds * self.sample_rate / Config.FRAME_LENGTH):
                if silent_frames > required_silent_frames:
                    print(" 🔇 (silence)", end="")
                    break
                if self.overflow_count > 3:
                    print(" ⚠️ (overflow)", end="")
                    break
                sd.sleep(50)

        print()  # Newline after recording
        if self.overflow_count > 0:
            print(f"⚠️ Audio overflow occurred {self.overflow_count} times")
        return np.concatenate(self.frames) if self.frames else np.array([])