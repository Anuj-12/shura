from numpy import float32
import sounddevice as sd 
import assistant
from config import TTS_CHANNELS, TTS_SAMPLE_RATE
from tts import speak, sample_rate
from stt import listen
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

print("Speak:")
while(True):
    prompt = listen(stream_in)
    #prompt = "Hello"
    
    while prompt is None:
        prompt = listen(stream_in)

    print(repr(prompt))
    for sentence in assistant.ask(prompt):
        speak(sentence, stream_out)
        full_resp += sentence

    assistant.update_history(prompt, full_resp)
    full_resp = ""

    if any(c == prompt.lower() for c in ["bye", "quit"]):
        stream_in.stop()
        stream_out.stop()
        break

