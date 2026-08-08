"""
Sample is one measurement of the mic
Frame contains all the samples for each channel

for Mono -> 1 frame = 1 sample
for Stereo -> 1 frame = 2 samples (Left channel, Right channel)
"""
import wave
import numpy as np
from typing import List
import sounddevice as sd
from faster_whisper import WhisperModel
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                    datefmt='%I:%M:%S %p',
                    force=True,
                    )

model_size = "medium.en"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

_transcription_done: bool = False;
capture_buffer: List = []

def record(frame) -> None:
    global capture_buffer
    # frames / sample_rate = seconds of audio
    # 1024 / 16_000 = 64ms of audio
    # This affects the latency and not the audio quality 
    # changed shit for debugging

    capture_buffer.append(frame)


def transcribe() -> str:
    global capture_buffer
    global _transcription_done
    _transcription_done = False

    logger.info("Transcribing")
    
    # Make all the individual signals a single signal
    audio = np.concatenate(capture_buffer, axis=0).squeeze()
    save_wav("debug.wav", audio)
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
        logger.info("Transcription Done")
        _transcription_done = False

        return True

    return False

def save_wav(filename: str, audio: np.ndarray, sample_rate: int = 16000):
    """
    Save a float32 numpy array in range [-1.0, 1.0] as a 16-bit PCM WAV.
    """

    # Flatten (Whisper expects mono anyway)
    audio = np.squeeze(audio)

    # Clip just in case
    audio = np.clip(audio, -1.0, 1.0)

    # Convert to int16 PCM
    pcm = (audio * 32767).astype(np.int16)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)       # mono
        wf.setsampwidth(2)       # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
