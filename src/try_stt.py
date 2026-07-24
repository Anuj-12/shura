import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

capture_buffer = [] 

stream = sd.InputStream(samplerate=16_000, channels=1)
stream.start()

model_size = "tiny.en"
# what is compute type?
model = WhisperModel(model_size, device="cpu", compute_type="int8")

frames, overflowed = stream.read(16_000)
#print(frames)
capture_buffer.append(frames)

# Each frame contains samples, so count up the samples in each frame
# If it is equal to sample rate, transfer the audio
samples = sum(chunk.shape[0] for chunk in capture_buffer)
if samples >= 16_000:
    print("Condition passed!")
    audio = np.concat(capture_buffer).squeeze()   # Returns a 1D array
    # Takes binaryIO, str, and ndarray
    segments, info = model.transcribe(audio, beam_size=5)
    for segment in segments:
        print("In for")
        print(segment.text)

# what is beam size?

