import sounddevice as sd 
import assistant
from speech import speak, sample_rate

# write → buffer → background thread → speakers

# print(type(voice.config))

stream = sd.OutputStream(samplerate=sample_rate, channels=1)

# Start and keep the stream open
# don't do it for every section of audio
stream.start()

assistant = assistant.Assistant()

full_resp = ""

while(True):
    prompt = input("> ")

    for sentence in assistant.ask(prompt):
        speak(sentence, stream)
        full_resp += sentence

    assistant.update_history(prompt, full_resp)

