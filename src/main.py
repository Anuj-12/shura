from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable
from collections import deque
from numpy import dtype, float32
import numpy as np
import sounddevice as sd 
import logging

from config import CHANNELS, FRAME_DURATION, STT_SAMPLE_RATE

import tts
import stt
import assistant
import vad

TTS_SAMPLE_RATE = tts.sample_rate

""" LOGGER CONFIG""" 
# Name of the logger = module name
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                    datefmt='%I:%M:%S %p',
                    force=True,
                    )

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
try:
    stream_out = sd.OutputStream(samplerate=TTS_SAMPLE_RATE, channels=CHANNELS, dtype=float32)
    stream_in = sd.InputStream(samplerate=STT_SAMPLE_RATE, channels=CHANNELS, dtype=float32)

    # Start and keep the stream open 
    stream_out.start()
    stream_in.start()
except Exception as e:
    logger.error("Error starting the stream: ", e)
    exit()

pre_buffer = deque(maxlen=40)

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
    stt.record(frame)
    prompt = stt.transcribe()

def respond(frame):
    global prompt
    global full_resp

    if not prompt.strip():
        return
    
    logger.info(repr(prompt))

    try:
        for sentence in assistant.ask(prompt):
            tts.speak(sentence, stream_out)
            full_resp += sentence
    except Exception as e:
        logger.error("Error generating ollama reponse:", e)

    if assistant.is_goodbye(prompt):
        logger.info("Exit sequence detected... exiting")

        stream_in.close()
        stream_out.close()
        exit()

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

    # Trying shit out
    frame = np.clip(frame * 2, -1.0, 1.0)

    if overflow:
        logger.warning("Capture frame overflow")

    if state == State.WAITING:
        if vad.detect_start(frame):
            event = Event.SPEECH_STARTED
    elif state == State.RECORDING:
        if vad.detect_end(frame):
            event = Event.SPEECH_ENDED
    elif state == State.TRANSCRIBING:
        if stt.transcription_done():
            event = Event.TRANSCRIPTION_ENDED
    elif state == State.RESPONDING:
        if assistant.response_done():
            event = Event.RESPONSE_DONE

    """ STATE TRANSITION LOGIC """
    logger.info(f"State- {state}, Event- {event}")
    # get() prevents KeyErrors
    transition = trans_table.get((state, event))
    if transition:
        if transition.action:
            logger.debug(f"Action- {transition.action.__name__}")
            transition.action(frame)

        state = transition.next_state
