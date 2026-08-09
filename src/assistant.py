from ollama import chat
from tools import ToolError
from tools.registry import get_tool_schemas
from tools.registry import TOOLS
from tools.filter import detect_tool
import config
import logging
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                    datefmt='%I:%M:%S %p',
                    force=True,
                    )

GOODBYE_PATTERNS = [
    r"^\s*(goodbye|bye|bye-bye)\s*[.!]?\s*$",
    r"^\s*(good night|goodnight)\s*[.!]?\s*$",
    r"^\s*(see you|see ya|see you later)\s*[.!]?\s*$",
]

_response_done = False
_history = []

def ask(prompt: str):
    global _response_done
    _response_done = False

    buffer = ""
    full_response = ""

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        # List unpacking 
        *_history,
        {"role": "user", "content": prompt},
    ]


    """ TOOL CALLING """
    tool_detect = detect_tool(prompt)

    if tool_detect:
        tool_check = chat(
            model=config.MODEL,
            stream=False,
            think=False,
            messages=messages,
            tools=get_tool_schemas()
        )

        if tool_check.message.tool_calls:
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
                    logger.error("Error in tool calling:", e)
        
    """ STREAMING BUFFER """
    stream = chat(
        model=config.MODEL,
        stream=True,
        think=False,
        messages=messages,
    )

    logger.debug(messages)

    for chunk in stream:
        msg = chunk.message.content
        if msg is None:
            continue

        full_response += msg
        buffer += msg

        if any(c in msg for c in ",.!?") and len(buffer) >= config.SPEECH_CHUNK_SIZE:
            yield buffer
            logger.info(repr(buffer));
            buffer = ""

    # flush remaining speech buffer
    if buffer:
        logger.info(repr(buffer));
        yield buffer

    _response_done = True

def update_history(user_msg: str, assistant_msg: str):
    _history.append({"role": "user", "content": user_msg})
    _history.append({"role": "assistant", "content": assistant_msg})

def response_done():
    # Fire it once like an interrupt
    global _response_done

    if _response_done:
        _response_done = False
        return True

    return False

def is_goodbye(prompt: str) -> bool:
    return any(
        re.search(pattern, prompt, re.IGNORECASE)
        for pattern in GOODBYE_PATTERNS
    )

