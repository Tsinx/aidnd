from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all tools in the Dungeons and Dragons game."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass

    @abstractmethod
    def get_briefing(self) -> str:
        """
        Returns a brief description of the tool's purpose and capabilities.
        This must be implemented by all subclasses.

        Returns:
            str: A string containing the tool's briefing.
        """
        pass

    @abstractmethod
    def get_required_parameters(self) -> str:
        """
        Returns a JSON schema string describing the parameters required by the execute method.
        This must be implemented by all subclasses.

        Returns:
            str: A string containing a JSON schema.
        """
        pass

    @abstractmethod
    def execute_with_parameters(self, parameters: dict) -> str:
        """
        Executes the tool with a dictionary of parameters.
        This must be implemented by all subclasses.

        Args:
            parameters: A dictionary of parameters for the tool.

        Returns:
            A string describing the result of the execution.
        """
        pass