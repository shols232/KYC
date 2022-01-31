from abc import ABC, abstractmethod
from typing import Any


class RequestClient(ABC):
    """Abstract class for Request clients."""

    @abstractmethod
    def run(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Abstract method for Request client run."""
