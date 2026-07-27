"""
Sample is one measurement of the mic
Frame contains all the samples for each channel

for Mono -> 1 frame = 1 sample
for Stereo -> 1 frame = 2 samples (Left channel, Right channel)
"""
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

from config import TTS_SAMPLE_RATE

model_size = "small.en"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

capture_buffer = []

def listen(stream: sd.InputStream):
    #print("Listening")
    # frames / sample_rate = seconds of audio
    # 1024 / 16_000 = 64ms of audio
    frames, overflowed = stream.read(1024)

    if overflowed:
        print("Audio Overflow")

    #print("Read Audio")
    capture_buffer.append(frames)

    # Each frame contains samples, so count up the samples in each frame
    # If it is equal to sample rate transfer the audio
    samples = sum(chunk.shape[0] for chunk in capture_buffer)
    if samples >= TTS_SAMPLE_RATE:
        #print("Calling Whisper")
        # Make all the individual signals a single signal
        audio = np.concatenate(capture_buffer, axis=0).squeeze()
        segments, info = model.transcribe(audio)
        print(f"{samples / TTS_SAMPLE_RATE:.2f} seconds")

        text = ""

        #print("Whisper Retured Generator")
       # Transciption only happens when iterating over segments
        for segment in segments:
            text += segment.text

        capture_buffer.clear()

        return text   
