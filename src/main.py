from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable
from collections import deque
from numpy import dtype, float32
import sounddevice as sd 

from config import CHANNELS, FRAME_DURATION, STT_SAMPLE_RATE

import tts
import stt
import assistant
import vad

TTS_SAMPLE_RATE = tts.sample_rate

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
stream_out = sd.OutputStream(samplerate=TTS_SAMPLE_RATE, channels=CHANNELS, dtype=float32)
stream_in = sd.InputStream(samplerate=STT_SAMPLE_RATE, channels=CHANNELS, dtype=float32)

# Start and keep the stream open 
stream_out.start()
stream_in.start()

pre_buffer = deque(maxlen=20)

""" FSM BASED IMPLEMENTATION """
state = State.WAITING

# Have to build the full response to append to the history
full_resp = ""
prompt = ""

def buffer_audio(frame):
    pre_buffer.append(frame)

def start_record(frame):
    stt.capture_buffer.extend(pre_buffer)
    pre_buffer.clear()

    stt.record(frame)

def record(frame):
    stt.record(frame)

def transcribe(frame):
    global prompt
    prompt = stt.transcribe()

def respond(frame):
    global prompt
    global full_resp

    if not prompt.strip():
        return
    
    print(repr(prompt))

    for sentence in assistant.ask(prompt):
        tts.speak(sentence, stream_out)
        full_resp += sentence

def update_history(frame):
    global full_resp
    assistant.update_history(prompt, full_resp)
    full_resp = ""

trans_table = {
        (State.WAITING, Event.EVENT_NONE):
        Transition(State.WAITING, buffer_audio),

        (State.WAITING, Event.SPEECH_STARTED):
        Transition(State.RECORDING, start_record),

        (State.RECORDING, Event.SPEECH_ENDED):
        Transition(State.TRANSCRIBING, transcribe),

        (State.RECORDING, Event.EVENT_NONE):
        Transition(State.RECORDING, record),

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
