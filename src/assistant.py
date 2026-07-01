from ollama import ChatResponse, chat
import config

class Assistant:
    def __init__(self):
        self.history = []

    def ask(self, prompt: str):
        buffer = ""
        full_response = ""

        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            # List unpacking 
            *self.history,
            {"role": "user", "content": prompt},
        ]

        print(messages)

        stream = chat(
            model=config.MODEL,
            stream=True,
            think=False,
            messages=messages,
        )

        for chunk in stream:
            msg = chunk.message.content
            if msg is None:
                continue

            full_response += msg
            buffer += msg

            if any(c in msg for c in ",.!?") or len(buffer) >= config.SPEECH_CHUNK_SIZE:
                yield buffer
                buffer = ""

        # flush remaining speech buffer
        if buffer:
            yield buffer

        # For mem update
        return full_response

    def update_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})

