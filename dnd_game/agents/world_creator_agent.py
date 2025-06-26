from .base import BaseAgent

class WorldCreatorAgent(BaseAgent):
    """Agent responsible for creating the game world and adventure setup."""

    def get_briefing(self) -> str:
        return "Creates a compelling game world, including a theme, key locations, and a starting quest hook, based on the player's ideas."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "world_idea": {"type": "string", "description": "A detailed description and complemention of the world the user wants to create."}
            },
            "required": ["world_idea"]
        }'''

    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """Generates a world based on the player's initial idea."""
        if stream_callback:
            stream_callback("**World Creator:** Crafting a new realm based on player's vision...\n")

        prompt = self._construct_prompt_with_parameters(parameters)
        return self._generate_response(prompt, stream_callback=stream_callback)

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        world_idea = parameters.get("world_idea", "")
        if self.history:
            latest_turn, past_history = self.history.get_history(k=5)
        else:
            latest_turn, past_history = "", ""
        """Constructs the prompt using the world idea and conversation history."""
        prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a world-building AI for a Dungeons & Dragons game. Your task is to create a compelling starting scenario. You must consider the ongoing conversation to ensure the world you create is consistent with what has already been discussed.

**Conversation History:**
{past_history}

**Latest Turn:**
{latest_turn}

**Player's Idea for the World:**
{world_idea}

Based on the history and the player's idea, describe the world's theme, a key location, and a starting quest hook. Keep it concise and engaging.

**World Description:**<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt