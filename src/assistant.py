from os import name
from ollama import chat
from tools import ToolError
from tools.registry import get_tool_schemas
from tools.registry import TOOLS
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

        #print(messages)

        """ TOOL CALLING """
        tool_check = chat(
            model=config.MODEL,
            stream=False,
            think=False,
            messages=messages,
            tools=get_tool_schemas()
        )

        if(tool_check.message.tool_calls):
            for tc in tool_check.message.tool_calls:
                # Get the tool's instance
                tool = TOOLS[tc.function.name]
                try:
                    result = tool.execute(tc.function.arguments)
                    messages.append({
                        'role': 'tool',
                        'tool_name': tc.function.name,
                        'content': str(result["result"])
                        })
                except ToolError as e:
                    messages.append({
                        'role': 'tool',
                        'tool_name': tc.function.name,
                        'content': "Tool failed to execute"
                        })
                except Exception as e:
                    print(e)

        
        """ STREAMING BUFFER """
        stream = chat(
            model=config.MODEL,
            stream=True,
            think=False,
            messages=messages,
            tools=get_tool_schemas()
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


