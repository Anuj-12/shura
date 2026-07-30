import webrtcvad
import config
import numpy as np
import sounddevice as sd

# Agressiveness mode for filtering non-speech
# 1- no filtering, 3 - high filtering
vad = webrtcvad.Vad(2)

speech_cnt = 0
silence_cnt = 0

# Stream captures frames as float32 and sends them over to VAD
# VAD converts to int16 and decides if the frame contains speech or just noise
# If VAD decides speech is present, the frame is sent to whisper
def detect_start(frame: np.ndarray) -> bool:
    global speech_cnt

    # because straight up .astype(int16) would give values
    # such as 0.6, 0.72 = 0, the largest 16 bit signed no. is 32768
    # so conversion with the product of float frame * 32767 gives a usable int frame
    frame = np.squeeze(frame)
    frame = (frame * 32767).astype(np.int16)
    vad_frame = frame.tobytes()
    curr_frame_is_speech = vad.is_speech(vad_frame, config.VAD_SAMPLE_RATE)

    if curr_frame_is_speech:
        speech_cnt += 1
    else:
        speech_cnt = 0

    return speech_cnt >= 7
    
def detect_end(frame: np.ndarray) -> bool:
    global silence_cnt

    # because straight up .astype(int16) would give values
    # such as 0.6, 0.72 = 0, the largest 16 bit signed no. is 32768
    # so conversion with the product of float frame * 32767 gives a usable int frame
    frame = np.squeeze(frame)
    frame = (frame * 32767).astype(np.int16)
    vad_frame = frame.tobytes()
    curr_frame_is_speech = vad.is_speech(vad_frame, config.VAD_SAMPLE_RATE)

    if curr_frame_is_speech:
        silence_cnt = 0
    else:
        silence_cnt += 1

    return silence_cnt >= 7
