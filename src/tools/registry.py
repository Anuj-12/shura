# Remove this after implementing decorators
from tools.date_time import DateTimeTool

TOOLS = {
        "date_time": DateTimeTool()
        }

def get_tool_schemas():
    tools = []
    for tool in TOOLS.values():
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
                }
            })

    return tools

