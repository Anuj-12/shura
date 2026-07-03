from abc import ABC, abstractmethod
# ABC -> Abstract Base Class

class ToolInterface(ABC):
    """ Interface that structures every tool """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON schema describing the tool's parameters."""
        pass

    @abstractmethod
    def execute(self, arguments:dict) -> dict:
        pass
