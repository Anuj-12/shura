
class ToolError(Exception):

    def __init__(self, message = "Tool use raised an error") -> None:
        self.message = message
        super().__init__(self.message)

