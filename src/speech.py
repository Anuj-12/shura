import config
from piper import PiperVoice

# write → buffer → background thread → speakers


voice = PiperVoice.load(config.VOICE_PATH)
sample_rate = voice.config.sample_rate
# print(type(voice.config))

def speak(msg: str, stream):
    for chunk in voice.synthesize(msg):
        # print(chunk)
        stream.write(chunk.audio_float_array)

