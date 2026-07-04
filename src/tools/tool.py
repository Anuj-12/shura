from abc import ABC, abstractmethod
from typing import Mapping, Any
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
    # Mapping = anything that behaves like a dictionary
    # Any = No type checking for that value
    def execute(self, arguments: Mapping[str, Any]) -> dict:
        pass
