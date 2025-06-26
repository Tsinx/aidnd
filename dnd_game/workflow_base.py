from abc import ABC, abstractmethod

class BaseWorkflow(ABC):
    """Abstract base class for all workflows."""

    def __init__(self, model: object, history: object):
        self.model = model
        self.history = history

    @abstractmethod
    def get_briefing(self) -> str:
        """Returns a brief description of what this workflow does."""
        pass

    @abstractmethod
    def get_required_parameters(self) -> str:
        """Returns a JSON schema describing the required parameters for the execute method."""
        pass

    @abstractmethod
    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """Executes the workflow's primary logic with parameters passed as a dictionary."""
        pass