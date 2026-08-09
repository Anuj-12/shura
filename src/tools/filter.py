import re

TOOL_PATTERNS = {
    "date_time": [
        r"\bwhat(?:'s| is)?\s+(?:the\s+)?time\b",
        r"\bcurrent\s+(?:date|time)\b",
        r"\bwhat\s+(?:day|date)\s+is\s+it\b",
        r"\btime\s+right\s+now\b",
        r"\bcurrent\s+time\b",
        r"\bcurrent\s+date\b",
        r"\bright\s+now\b.*\btime\b",
    ],
}

def detect_tool(prompt: str) -> str | None:
    for tool_name, patterns in TOOL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return tool_name

    return None

