from .base import BaseAgent

class StoryTellerAgent(BaseAgent):
    """Agent responsible for progressing the story based on player actions."""

    def get_briefing(self) -> str:
        return "Generates the next part of the story based on the player's action. It describes the outcome and moves the narrative forward."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "player_action": {"type": "string", "description": "The specific action the player wants to take. e.g., 'I attack the goblin' or 'I try to persuade the guard'"}
            },
            "required": ["player_action"]
        }'''

    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """Generates the next part of the story based on player action."""
        if stream_callback:
            stream_callback("**Story Teller:** Weaving the consequences of the player's actions...\n")

        prompt = self._construct_prompt_with_parameters(parameters)
        return self._generate_response(prompt, stream_callback=stream_callback)

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        player_action = parameters.get("player_action", "")
        if self.history:
            latest_turn, past_history = self.history.get_history(k=5)
        else:
            latest_turn, past_history = "", "The story has just begun."
        """Constructs the prompt for the story teller."""
        prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are the story engine for a Dungeons & Dragons game. Your role is to take the player's action and the story so far, and generate the outcome. You should describe what happens as a result of the player's action, but DO NOT speak directly to the player. You are generating context for the Dungeon Master.

**Past Events:**
{past_history}

**Latest Turn:**
{latest_turn}

**Player Action:** {player_action}

**Outcome:**<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt