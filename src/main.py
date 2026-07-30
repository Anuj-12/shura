from dataclasses import dataclass
from numpy import dtype, float32
from enum import Enum, auto
import sounddevice as sd 
from typing import Callable

import assistant
from config import FRAME_DURATION, TTS_CHANNELS, TTS_SAMPLE_RATE
import tts
import stt
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

trans_table = {
    (State.WAITING, Event.SPEECH_STARTED):
        Transition(State.RECORDING, start_recording),

    (State.RECORDING, Event.SPEECH_ENDED):
        Transition(State.TRANSCRIBING, stop_recording),

    (State.TRANSCRIBING, Event.TRANSCRIPTION_ENDED):
        Transition(State.RESPONDING, respond),

    (State.RESPONDING, Event.RESPONSE_DONE):
        Transition(State.WAITING, reset),
}


""" STREAM CONFIGURATION """

stream_out = sd.OutputStream(samplerate=TTS_SAMPLE_RATE, channels=1)
stream_in = sd.InputStream(samplerate=TTS_SAMPLE_RATE, channels=TTS_CHANNELS, dtype=float32)

# Start and keep the stream open 
stream_out.start()
stream_in.start()


""" FSM BASED IMPLEMENTATION """

state = State.WAITING

assistant = assistant.Assistant()
speech_counter = 0

full_resp = ""
capture_buffer = []

print("Speak:")
while(True):
    """ POLLING FOR EVENTS """
    frame, overflow = stream_in.read(FRAME_DURATION)

    event : Event = Event.EVENT_NONE

    if vad.detect_start(frame):
        event = Event.SPEECH_STARTED

    if vad.detect_end(frame):
        event = Event.SPEECH_ENDED

    """ STATE TRANSITION LOGIC """
    transition = trans_table.get((state, event))
    if transition:
        if transition.action:
            transition.action(frame)

        state = transition.next_state

