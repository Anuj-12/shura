from config import ENG_VOICE_PATH
from piper import PiperVoice
import sounddevice as sd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                    datefmt='%I:%M:%S %p',
                    force=True,
                    )

voice = PiperVoice.load(ENG_VOICE_PATH)
sample_rate = voice.config.sample_rate
# print(type(voice.config))

def speak(msg: str, stream):
    try:
        for chunk in voice.synthesize(msg):
            # print(chunk)
            stream.write(chunk.audio_float_array)
    except Exception as e:
        logger.error("TTS failed:", e)

