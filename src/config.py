MODEL = "gemma3:4b"

NAME = "Shura"

SYSTEM_PROMPT = f"""
You are {NAME}, a personal AI assistant.

You are concise, practical, and technically knowledgeable.
You prefer short but polite answers unless asked for detail.
You do suggest the next practical follow up question.
You are running locally on the user's laptop.
You can admit uncertainty.
"""

# PIPER CONFIG

VOICE_PATH = "voices/en_GB-alba-medium.onnx"


VOLUME=0.5,  # half as loud
LENGTH_SCALE=1.0,  # speed x1
NOISE_SCALE=1.0,  # more audio variation
NOISE_W_SCALE=1.0,  # more speaking variation
NORMALIZE_AUDIO=False, # use raw audio from voice
