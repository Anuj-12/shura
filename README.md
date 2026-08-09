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

## Demo
https://github.com/user-attachments/assets/ebcf215f-4cd3-4321-8d17-74a8ca6eb5a1

## Known Issues

* Tool calls can occasionally produce inconsistent responses depending on the local LLM.
* Goodbye detection has a few false negatives for less common phrasing.
* The TTS cleanup is intentionally lightweight and may not handle every form of Markdown formatting.
* The visualizer/web UI is not included yet and will be developed separately.
