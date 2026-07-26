from numpy import float32
from pydantic import ValidationError
import sounddevice as sd 
import assistant
from config import TTS_CHANNELS, TTS_SAMPLE_RATE
from tts import speak, sample_rate
from stt import listen
from vad import is_speech
from enum import Enum

# write → buffer → background thread → speakers

#class States(Enum):
#    IDLE = 0
#    LISTENING = 1t
#    THINKING = 2
#    SPEAKING = 3
#    TOOL_USE = 4

#state = States.IDLE

# Start and keep the stream open 
stream_out = sd.OutputStream(samplerate=sample_rate, channels=1)
stream_out.start()

stream_in = sd.InputStream(samplerate=TTS_SAMPLE_RATE, channels=TTS_CHANNELS, dtype=float32)
stream_in.start()

assistant = assistant.Assistant()

full_resp = ""

capture_buffer = []
frame_duration = 480

print("Speak:")
while(True):
    frame, overflowed = stream_in.read(frame_duration)
    # print(frame.dtype)
    # print(frame.shape)
    if(overflowed):
        print("Audio overflowed")


    if(is_speech(frame)):
        print("Speech detected")
        prompt = listen(stream_in)
    else:
        print("Speech not detected")
        continue
    prompt = "Hello, what is your name? I think you are my PA... what is the time then?"

    if prompt is None:
        continue

    # repr prints the string with '\n' and stuff
    print(repr(prompt))
    for sentence in assistant.ask(prompt):
        speak(sentence, stream_out)
        full_resp += sentence

    assistant.update_history(prompt, full_resp)
    print(full_resp)
    full_resp = ""

    if any(c == prompt.lower() for c in ["bye", "quit"]):
        stream_in.stop()
        stream_out.stop()
        break

