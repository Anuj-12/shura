from dataclasses import dataclass
from numpy import dtype, float32, full
from enum import Enum, auto
import sounddevice as sd 
from typing import Callable

from config import CHANNELS, FRAME_DURATION, SAMPLE_RATE 

import tts
import stt
import assistant
import vad

# write → buffer → background thread → speakers

""" FSM CONFIGURATION """
class State(Enum):
    WAITING = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    RESPONDING = auto()

class Event(Enum):
    SPEECH_STARTED = auto()
    SPEECH_ENDED = auto()
    TRANSCRIPTION_ENDED = auto()
    RESPONSE_DONE = auto()
    EVENT_NONE = auto()

# Makes it behave like struct
@dataclass()
class Transition:
    next_state:  State
    action: Callable | None = None


""" STREAM CONFIGURATION """
stream_out = sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS)
stream_in = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=float32)

# Start and keep the stream open 
stream_out.start()
stream_in.start()


""" FSM BASED IMPLEMENTATION """
state = State.WAITING

# Have to build the full response to append to the history
full_resp = ""
prompt = ""

def record(frame):
    stt.record(frame)

def transcribe(frame):
    global prompt
    prompt = stt.transcribe()

def respond(frame):
    global prompt
    global full_resp
    print(repr(prompt))

    for sentence in assistant.ask(prompt):
        tts.speak(sentence, stream_out)
        full_resp += sentence

    print(full_resp)

def update_history(frame):
    assistant.update_history(prompt, full_resp)

trans_table = {
    (State.WAITING, Event.SPEECH_STARTED):
        Transition(State.RECORDING, record),

    (State.RECORDING, Event.SPEECH_ENDED):
        Transition(State.TRANSCRIBING, transcribe),

    (State.TRANSCRIBING, Event.TRANSCRIPTION_ENDED):
        Transition(State.RESPONDING, respond),

    (State.RESPONDING, Event.RESPONSE_DONE):
        Transition(State.WAITING, update_history),
}

print("Speak:")
while(True):
    """ POLLING FOR EVENTS """
    event: Event = Event.EVENT_NONE
    frame, overflow = stream_in.read(FRAME_DURATION)

    if vad.detect_start(frame):
        event = Event.SPEECH_STARTED
    elif vad.detect_end(frame):
        event = Event.SPEECH_ENDED
    elif stt.transcription_done():
        event = Event.TRANSCRIPTION_ENDED;
    elif assistant.response_done():
        event = Event.RESPONSE_DONE

    """ STATE TRANSITION LOGIC """
    # get() prevents KeyErrors
    transition = trans_table.get((state, event))
    if transition:
        if transition.action:
            transition.action(frame)

        state = transition.next_state

    if state == State.RECORDING:
        record(frame)
