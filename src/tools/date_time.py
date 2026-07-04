from datetime import datetime
from tools import tool

class DateTimeTool(tool.ToolInterface):
    @property
    def name(self) -> str:
        return "date_time"

    @property
    def description(self) -> str:
        return "Returns the current local date, time and day of the week."

    @property
    def parameters(self) -> dict:
        """JSON schema describing the tool's parameters."""
        return {
                # type = type of argument llm should send
                "type": "object",
                "properties": {},
                "required": []
                }

    def execute(self, arguments:dict) -> dict:

        now = datetime.now()

        return {
            "success": True,
            "result": {
                "date": now.strftime("%d-%m-%Y"),
                "time": now.strftime("%I:%M %p"),
                "weekday": now.strftime("%A"),
            }
        }
