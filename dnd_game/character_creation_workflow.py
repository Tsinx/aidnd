import re
import json
import logging
from json_repair import repair_json
from .workflow_base import BaseWorkflow
from .agents.character_creation_planner_agent import CharacterCreationPlannerAgent
from .agents.executor_agent import ExecutorAgent
from .agents.tool_caller_agent import ToolCallerAgent
from .tools.character_tools import CreateCharacterTool, EditCharacterTool, AddToCharacterListAttributeTool, RemoveFromCharacterListAttributeTool, CreateAndGiveItemTool, EquipItemTool
from .game_engine.character import Character

class CharacterCreationWorkflow(BaseWorkflow):
    """Manages the character creation process using a Planner -> Executor -> Tool Caller pipeline."""

    def __init__(self, model: object, history: object, game_state: object, thoughts_container: object, k=5):
        super().__init__(model, history)
        self.game_state = game_state
        self.thoughts_container = thoughts_container
        self.k = k

        character_template = Character.get_template()
        # Get all characters during initialization
        self.all_characters = self.game_state.characters

        # The player_characters list will be filtered dynamically at execution time
        self.agents = {
            "PlannerAgent": CharacterCreationPlannerAgent(model, self.history, character_template, [], k=self.k),
            "ExecutorAgent": ExecutorAgent(model, k=self.k),
            "ToolCallerAgent": ToolCallerAgent(model, k=self.k),
        }

        self.tools = {
            tool.name: {"agent": tool, "briefing": tool.get_briefing()}
            for tool in [
                CreateCharacterTool(),
                EditCharacterTool(),
                AddToCharacterListAttributeTool(),
                RemoveFromCharacterListAttributeTool(),
                CreateAndGiveItemTool(),
                EquipItemTool(),
            ]
        }

    def get_briefing(self) -> str:
        return "Guides the user through character creation, including setting background, stats, buffs, items, and equipment."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "creation_guidance": {"type": "string", "description": "The user's guidance or request for character creation."}
            },
            "required": ["creation_guidance"]
        }'''

    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        # here stream_callback is not used in the following part, just to keep the same interface as the base class and agent

        creation_guidance = parameters.get("creation_guidance")

        # Dynamically filter for player characters at the time of execution
        player_characters = [char for char in self.all_characters if char.is_player]
        self.agents["PlannerAgent"].update_player_characters(player_characters)
        sidebar_writer = self._get_stream_writer(self.thoughts_container)

        available_tools = [
            {"name": name, "briefing": data["briefing"]}
            for name, data in self.tools.items()
        ]

        main_memory = [f"User's character creation guidance: {creation_guidance}"]
        max_turns = 15

        for i in range(max_turns):
            sidebar_writer(f"\n--- **Creation Loop {i+1} / {max_turns}** ---\n")

            planner_params = {
                "available_tools": available_tools,
                "scratchpad": "\n".join(main_memory),
                "current_turn": i + 1,
                "max_turns": max_turns,
                "guidance": creation_guidance
            }
            plan_text = self.agents["PlannerAgent"].execute_with_parameters(
                parameters=planner_params,
                stream_callback=sidebar_writer
            )
            main_memory.append(f"**Planner's Plan:**\n{plan_text}")

            executor_params = {
                "planner_output": plan_text,
                "scratchpad": "\n".join(main_memory),
                "available_tools": available_tools
            }
            executor_output = self.agents["ExecutorAgent"].execute_with_parameters(
                parameters=executor_params,
                stream_callback=sidebar_writer
            )

            executor_command = self._extract_json(executor_output)
            if not executor_command or "current_execution" not in executor_command:
                sidebar_writer("**Error:** Executor failed to produce a valid command. Aborting.")
                break

            execution_status = executor_command.get("current_execution")
            tool_name = executor_command.get("tool_name")

            sidebar_writer(f"**Executor's Action:** `{execution_status}`")
            if tool_name:
                sidebar_writer(f" on Tool: `{tool_name}`")
            sidebar_writer("\n")

            if execution_status in ["task_complete", "ask_for_user_input"]:
                sidebar_writer(f"**Info:** Loop ending. Reason: {execution_status}.")
                break
            
            if execution_status == "idle":
                sidebar_writer("**Info:** Executor is idle. Continuing to next loop.")
                continue

            if execution_status == "call_tool":
                if not tool_name or tool_name not in self.tools:
                    sidebar_writer(f"**Error:** Executor chose an invalid tool: `{tool_name}`. Aborting.")
                    break
                
                target_tool = self.tools[tool_name]["agent"]

                try:
                    params_schema_str = target_tool.get_required_parameters()
                    params_schema = json.loads(repair_json(params_schema_str))
                    required_params = params_schema.get("required", [])
                except (json.JSONDecodeError, ValueError) as e:
                    sidebar_writer(f"**Error:** Could not parse parameters schema for `{tool_name}`: {e}")
                    break

                filled_params = {}
                if required_params:
                    temporary_memory = main_memory + [f"**Executor's Decision:**\n{executor_output}"]
                    
                    tool_caller_params = {
                        "scratchpad": "\n".join(temporary_memory),
                        "tool_to_call": tool_name,
                        "tool_params_schema": params_schema_str
                    }
                    tool_caller_output = self.agents["ToolCallerAgent"].execute_with_parameters(
                        parameters=tool_caller_params,
                        stream_callback=sidebar_writer
                    )

                    filled_params = self._extract_json(tool_caller_output)
                    if filled_params is None:
                        sidebar_writer(f"**Error:** Tool Caller failed to produce valid JSON for `{tool_name}`. Aborting.")
                        break

                tool_result = target_tool.execute_with_parameters(filled_params, self.game_state)
                main_memory.append(f"**Tool Output for `{tool_name}`:**\n{tool_result}")

        final_output = main_memory[-1] 
        yield final_output

    def _get_stream_writer(self, container):
        if not container:
            return lambda text: None
        buffer = ""
        placeholder = container.empty()
        def writer(text):
            nonlocal buffer
            buffer += text
            placeholder.markdown(buffer)
        return writer

    def _extract_json(self, text: str) -> dict:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*)', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(repair_json(json_str))
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse JSON: {e}\nRaw string: {json_str}")
                return None
        return None