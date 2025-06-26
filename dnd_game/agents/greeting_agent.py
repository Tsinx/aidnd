import logging
from .base import BaseAgent

class GreetingAgent(BaseAgent):
    """An agent that handles greetings and guides the player on how to play the game."""

    def get_briefing(self) -> str:
        return "Handles non-game-related inputs like greetings or small talk. It provides guidance to the player on how to start or continue the game, for example, by suggesting to first build the world and then create a character."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {},
            "required": []
        }'''



    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """Generates a helpful message to guide the player."""
        logging.info(f"Executing GreetingAgent with parameters: {parameters}")
        prompt = self._construct_prompt_with_parameters(parameters)
        response = self._generate_response(prompt, stream_callback=stream_callback)
        return response

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        """Constructs the prompt for the greeting agent."""
        if self.history:
            latest_turn, history = self.history.get_history(k=self.k)
        else:
            latest_turn, history = "", ""
        
        return f"""
You are a friendly and helpful guide for a Dungeons & Dragons game. The player has sent a message that seems unrelated to the current game state.

**Conversation History:**
{history}

**Player's Latest Message:**
'{latest_turn}'

Your task is to provide a concise, polite, and constructive response to guide the player. 
- If the game has not started, suggest the next step, like creating the game world or a character.
- If the game is in progress, gently guide them back to the story.

Keep your response short and to the point.
"""