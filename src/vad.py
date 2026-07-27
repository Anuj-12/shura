import webrtcvad
import config
import numpy as np
import sounddevice as sd

# Agressiveness mode for filtering non-speech
# 1- no filtering, 3 - high filtering
vad = webrtcvad.Vad(2)

# Stream captures frames as float32 and sends them over to VAD
# VAD converts to int16 and decides if the frame contains speech or just noise
# If VAD decides speech is present, the frame is sent to whisper
def is_speech(frame: np.ndarray) -> bool:
    frame = (frame * 32767).astype(np.int16)
    frame = np.squeeze(frame)
    # print(frame.dtype)
    # print(frame.shape)
    vad_frame = frame.astype(np.int16).tobytes()
    return vad.is_speech(vad_frame, config.VAD_SAMPLE_RATE)
