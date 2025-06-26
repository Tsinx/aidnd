from .base import BaseAgent
import json

class CharacterCreationPlannerAgent(BaseAgent):
    """An agent that creates a plan to guide the user through character creation."""

    def __init__(self, model: object, history: object, character_template: dict, player_characters: list, k=5):
        super().__init__(model, k=k)
        self.history = history
        self.character_template = character_template
        self.player_characters = player_characters

    def update_player_characters(self, player_characters: list):
        """Updates the list of player characters."""
        self.player_characters = player_characters

    def get_briefing(self) -> str:
        return "I am a planner agent for character creation. My job is to create a plan to guide the user through the character creation process, using a character template and the list of existing player characters as context."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "available_tools": {"type": "array", "description": "The tools available for character creation."},
                "scratchpad": {"type": "string", "description": "The current state of the character creation process."},
                "current_turn": {"type": "integer", "description": "The current turn number."},
                "max_turns": {"type": "integer", "description": "The maximum number of turns."},
                "guidance": {"type": "string", "description": "The user's guidance for character creation."}
            },
            "required": ["available_tools", "scratchpad", "current_turn", "max_turns", "guidance"]
        }'''

    def get_prompt(self, available_tools: list, scratchpad: str, current_turn: int, max_turns: int, guidance: str) -> str:
        conversation_history = self.history.get_full_history()
        return f'''
Your role is to act as a master planner for a Dungeons & Dragons character creation assistant. Your goal is to create a step-by-step plan to respond to the user's guidance and create a complete character.

**Character Template (Structure to follow):**
```json
{json.dumps(self.character_template, indent=2)}
```

**Existing Player Characters:**
{self._format_characters(self.player_characters)}

**Conversation History:**
{conversation_history}

**Available Tools for Character Creation:**
{self._format_tools(available_tools)}

**Creation Progress (Scratchpad):**
{scratchpad}

**User's Guidance for Creation:**
{guidance}

**Your Task:**
Based on the user's guidance, the character template, the conversation history, and the creation progress, create a concise, step-by-step plan. Your plan should lead to a complete and well-defined character that is distinct from existing characters. You are on turn {current_turn} of {max_turns}.

**Planning Guidelines:**
1.  **Analyze Guidance:** Break down the user's guidance. What are the key specifications for the new character?
2.  **Compare with Template:** Use the template as a checklist. Which fields need to be filled?
3.  **Consult the Scratchpad:** Review what has already been created. What is the next logical step to fulfill the user's guidance?
4.  **Ensure Uniqueness:** Look at the list of existing characters. The new character's name must be unique.
5.  **Select Tools:** Identify which tools are best suited to execute the plan. Your plan should explicitly state which tool to use for each step (e.g., `CreateCharacterTool` to start, `EditCharacterTool` for attributes).
6.  **Formulate the Plan:** Write a clear, numbered list of actions. Each step should be a single, actionable instruction for the 'Executor' agent.

**Output Format:**
Begin your response with your thought process, then provide the plan in a numbered list.

Now, create your plan for the current situation.
'''

    def _format_characters(self, characters: list) -> str:
        if not characters:
            return "- None"
        return "\n".join([f"- **{c.name}** ({c.character_class}, Level {c.level})" for c in characters])

    def _format_tools(self, tools: list) -> str:
        return "\n".join([f"- **{tool['name']}**: {tool['briefing']}" for tool in tools])