# Shura

Shura is a local-first voice AI assistant built in Python.

The goal of the project is to create a fast, modular assistant that runs entirely on local hardware while remaining easy to extend.

## Current Features

* 🎙️ Speech-to-Text (Faster Whisper)
* 🗣️ Text-to-Speech (Piper)
* 🧠 Local LLM inference (Ollama)
* 🛠️ Tool calling
* 🎧 Voice Activity Detection (WebRTC VAD)
* ⚡ Streaming responses

## Planned

* Conversation state machine
* Wake word detection
* Memory
* Vision support
* Additional tools
* Improved speech interruption handling
* German conversation mode

## Tech Stack

* Python
* Ollama
* Faster Whisper
* Piper
* WebRTC VAD
* SoundDevice
* NumPy

## Status

This project is actively under development and the architecture is evolving as new features are added.

## Known Issues

- STT may occasionally stop detecting speech until restarted.
- First word of an utterance may be clipped.
- Tool selection is still conservative and occasionally unnecessary.
