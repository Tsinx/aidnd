import json
from .base import BaseAgent

class ToolCallerAgent(BaseAgent):
    """An agent that prepares the parameters for a tool call."""

    def get_briefing(self) -> str:
        return "Fills in the required JSON parameters for a specific tool based on the conversation history and context."

    def get_required_parameters(self) -> str:
        # This agent is called internally by the workflow.
        return "{}"

    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """Generates the parameters for the specified tool."""
        prompt = self._construct_prompt_with_parameters(parameters)
        tool_to_call = parameters.get("tool_to_call", "")
        if stream_callback:
            stream_callback(f"\n### Tool Caller Agent Thinking (for {tool_to_call})...\n")
        return self._generate_response(prompt, stream_callback=stream_callback)

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        scratchpad = parameters.get("scratchpad", "")
        tool_to_call = parameters.get("tool_to_call", "")
        tool_params_schema = parameters.get("tool_params_schema", "{}")
        """Constructs the prompt for the tool caller agent."""
        prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are the Tool Caller, a specialized agent within a Dungeons & Dragons AI system. Your job is to take a decision to call a tool and prepare the exact parameters needed for that tool to function.

**Your Context:**
- **Scratchpad:** The full history of the current turn, including the user's request, the Planner's high-level plan, and the Executor's decision to call a specific tool.
- **Tool to Call:** The name of the tool that the Executor has decided to use.
- **Tool's Parameter Schema:** A JSON object describing the parameters the tool requires.

**Your Task:**
1.  **Think Step-by-Step:** First, write down your reasoning. Carefully analyze the entire scratchpad to understand the context and the user's intent. Look at the parameter schema for the target tool.
2.  **Output a JSON Object:** After your reasoning, you MUST output a JSON object enclosed in ```json ... ```. This JSON object must be the complete and valid set of parameters required by the tool. The keys and value types must match the provided schema exactly.

**Contextual Information:**

**Full Turn Scratchpad:**
{scratchpad}

**Tool to Call:**
`{tool_to_call}`

**Required Parameters Schema for `{tool_to_call}`:**
```json
{tool_params_schema}
```

---

### Your Reasoning (Chain of Thought)
*(Think here... Based on the scratchpad, what are the correct values for the parameters: {list(json.loads(tool_params_schema).keys())}?)*

```json
{{
    // Fill in the parameters for the tool here
}}
```<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt