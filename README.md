# Shura

Shura is a fully local AI voice assistant that I built in Python - VAD senses you talking, she listens, calls a tool if she *actually* needs to and speaks her response out loud. Every part of this is offline, so no API bills to be dealt with 🥳.

## Current Features

* **Talks back while she's still thinking** -- responses stream and get spoken sentence-by-sentence instead of waiting for the full reply
* **Short-term memory** -- a single session of conversation builds its context as you continue to chat
* **Reaches for tools only when she actually needs to** -- most questions are answered straight from the model, without unnecessary tool calls
* **Fully offline** -- Whisper, Ollama, and Piper all run locally; nothing leaves your machine
* **Built on an explicit state machine** -- every stage of a conversation (listening, recording, transcribing, responding) is a separate, debuggable state

## Planned

* Wake word detection
* Long-term memory
* Vision support
* Additional tools
* Speech interruption handling
* German conversation mode (for practicing)

## Tech Stack

* **Python**
* **Ollama + llama3.1:8b** — local LLM inference
* **Faster Whisper** — speech-to-text
* **Piper** — text-to-speech
* **WebRTC VAD** — voice activity detection
* **SoundDevice** — audio input/output
* **NumPy** — audio processing

## How it works

Shura runs on a state machine with four stages: waiting, recording, transcribing, and responding. She's idle and buffering audio until WebRTC VAD detects you've started talking, at which point she starts recording — and keeps recording until VAD detects you've stopped. That audio gets transcribed locally with Faster Whisper, sent to a local Ollama model (with a quick check for whether a tool call is actually needed), and the response streams back sentence-by-sentence through Piper as it's generated, so she starts speaking before the full reply is even ready.

## Requirements

1. Python 3.11+
2. [Ollama](https://ollama.com) installed and running locally
3. Model pulled: `ollama pull llama3.1:8b`
4. PortAudio installed on Linux for `sounddevice`: `sudo apt install libportaudio2`
5. Runs locally on CPU; Faster Whisper uses the configured compute type for speech recognition

## Usage

### Installation

## Installation
```bash
git clone https://github.com/Anuj-12/shura
cd shura_ai

# Create the environment and install dependencies
uv sync

# Activate the environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Pull the local model
ollama pull llama3.1:8b
```

Change the name of the user in config.py and run by using:
```bash
uv run src/main.py
```


## Demo
https://github.com/user-attachments/assets/ebcf215f-4cd3-4321-8d17-74a8ca6eb5a1

## Known Issues

* Tool calls can occasionally produce inconsistent responses depending on the local LLM.
* Goodbye detection has a few false negatives for less common phrasing.
* The TTS cleanup is intentionally lightweight and may not handle every form of Markdown formatting.
* The visualizer/web UI is not included yet and will be developed separately.
