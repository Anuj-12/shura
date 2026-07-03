import sounddevice as sd 
import assistant
from speech import speak, sample_rate
from enum import Enum


# write → buffer → background thread → speakers

#class States(Enum):
#    IDLE = 0
#    LISTENING = 1
#    THINKING = 2
#    SPEAKING = 3
#    TOOL_USE = 4

#state = States.IDLE


# Start and keep the stream open 
stream = sd.OutputStream(samplerate=sample_rate, channels=1)
stream.start()

assistant = assistant.Assistant()

full_resp = ""

while(True):
    prompt = input("> ")

    for sentence in assistant.ask(prompt):
        speak(sentence, stream)
        full_resp += sentence

    assistant.update_history(prompt, full_resp)
    full_resp = ""

    if any(c == prompt.lower() for c in ["bye", "quit"]):
        break

