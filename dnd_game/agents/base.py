from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dnd_game.history import ConversationHistory



class BaseAgent(ABC):
    """Abstract base class for all agents in the Dungeons and Dragons game."""

    def __init__(self, model, k=5):
        self.model = model
        self.history = None
        self.k = k

    def set_history(self, history: object):
        """Sets the conversation history for the agent."""
        self.history = history

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
    def get_briefing(self) -> str:
        """
        Returns a brief description of the agent's purpose and capabilities.
        This must be implemented by all subclasses.

        Returns:
            str: A string containing the agent's briefing.
        """
        pass



    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """
        Executes the agent with a dictionary of parameters.
        This method relies on the subclass implementing _construct_prompt_with_parameters.
        """
        prompt = self._construct_prompt_with_parameters(parameters)
        return self._generate_response(prompt, stream_callback=stream_callback)

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        """
        Constructs a prompt from a dictionary of parameters.
        This is a generic implementation and should be overridden by subclasses if specific
        prompt engineering is needed.
        """
        prompt = "Please perform your task with the following information:\n\n"
        for key, value in parameters.items():
            prompt += f"{key}: {value}\n"
        return prompt

    def _generate_response(self, prompt, max_tokens=8192, stream_callback=None):
        """Helper method to generate a response from the language model."""
        response_stream = self.model(
            prompt,
            max_tokens=max_tokens,
            stop=None,  # GGUF models handle stopping internally or via specific tokens
            temperature=0.1, # Lower temperature to reduce randomness
            echo=False,
            stream=True  # Always stream to handle callbacks
        )

        full_response = ""
        for chunk in response_stream:
            text_chunk = chunk['choices'][0]['text']
            full_response += text_chunk
            if stream_callback:
                stream_callback(text_chunk)

        # Log the full response for debugging purposes, especially for tool callers
        logging.info(f"Agent {self.__class__.__name__} generated response: {full_response}")

        # whether the chunk is streamed to the front end, return a full response to back end
        return full_response