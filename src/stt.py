"""
Sample is one measurement of the mic
Frame contains all the samples for each channel

for Mono -> 1 frame = 1 sample
for Stereo -> 1 frame = 2 samples (Left channel, Right channel)
"""
from typing import List
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

model_size = "small.en"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

capture_buffer: List = []

def start_recording(stream: sd.InputStream):
    global capture_buffer
    # frames / sample_rate = seconds of audio
    # 1024 / 16_000 = 64ms of audio
    # This affects the latency and not the audio quality 
    frames, overflowed = stream.read(1024)

    if overflowed:
        print("Audio Overflow")

    capture_buffer.append(frames)


def stop_recording():
    global capture_buffer
    
    # Make all the individual signals a single signal
    audio = np.concatenate(capture_buffer, axis=0).squeeze()
    segments, info = model.transcribe(audio)

    text = ""

    # Transciption only happens when iterating over segments
    for segment in segments:
        text += segment.text
        
    capture_buffer.clear()

    return text   
