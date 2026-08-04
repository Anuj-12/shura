from config import ENG_VOICE_PATH
from piper import PiperVoice
import sounddevice as sd

voice = PiperVoice.load(ENG_VOICE_PATH)
sample_rate = voice.config.sample_rate
# print(type(voice.config))

def speak(msg: str, stream):
    for chunk in voice.synthesize(msg):
        # print(chunk)
        stream.write(chunk.audio_float_array)

