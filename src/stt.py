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

model_size = "medium.en"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

_transcription_done: bool = False;
capture_buffer: List = []

def record(stream: sd.InputStream) -> None:
    global capture_buffer
    # frames / sample_rate = seconds of audio
    # 1024 / 16_000 = 64ms of audio
    # This affects the latency and not the audio quality 
    frames, overflowed = stream.read(1024)

    if overflowed:
        print("Audio Overflow")

    capture_buffer.append(frames)


def transcribe() -> str:
    global capture_buffer
    global _transcription_done
    _transcription_done = False
    
    # Make all the individual signals a single signal
    audio = np.concatenate(capture_buffer, axis=0).squeeze()
    segments, info = model.transcribe(audio)

    text = ""

    # Transciption only happens when iterating over segments
    for segment in segments:
        text += segment.text
        
    capture_buffer.clear()
    _transcription_done = True
    
    return text   

def transcription_done() -> bool:
    global _transcription_done

    if _transcription_done:
        _transcription_done = False
        return True

    return False

