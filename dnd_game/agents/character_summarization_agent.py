from .base import BaseAgent

class CharacterSummarizationAgent(BaseAgent):
    """Summarizes the character creation process and extracts the final character details."""

    def get_briefing(self) -> str:
        return "Summarizes the entire character creation log into a final, clean character sheet."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "creation_log": {"type": "string", "description": "The full log of the character creation process, including all plans, actions, and tool outputs."}
            },
            "required": ["creation_log"]
        }'''

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        creation_log = parameters.get("creation_log", "")

        prompt = f"""You are a meticulous scribe tasked with creating a final character sheet from a detailed creation log.
Review the entire log provided below, which includes the user's guidance, the planner's thoughts, executor's actions, and tool outputs.
Your goal is to synthesize all this information into a single, clean, and comprehensive JSON object representing the final state of the character.

**Creation Log:**
{creation_log}

**Your Task:**
Based on the log, generate a JSON object that describes the character. The JSON should include all relevant attributes such as name, background, stats, class, skills, inventory, and equipment. 
If the character creation was not successfully completed, return a JSON object with a single key "error" describing why it failed.
Present the final character sheet as a single JSON object.
"""
        return prompt

    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        prompt = self._construct_prompt_with_parameters(parameters)
        response = self._generate_response(
            prompt=prompt,
            stream_callback=stream_callback
        )
        return response