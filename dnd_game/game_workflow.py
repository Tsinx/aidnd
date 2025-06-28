import re
import json
import logging
from json_repair import repair_json
from .agents.world_creator_agent import WorldCreatorAgent

from .agents.story_teller_agent import StoryTellerAgent
from .agents.narrative_agent import NarrativeAgent
from .agents.planner_agent import PlannerAgent
from .agents.executor_agent import ExecutorAgent
from .agents.tool_caller_agent import ToolCallerAgent
from .agents.greeting_agent import GreetingAgent
from .history import ConversationHistory
from .workflow_base import BaseWorkflow
from .character_creation_workflow import CharacterCreationWorkflow

class GameWorkflow(BaseWorkflow):
    """Manages the overall game flow and agent interactions using a Planner -> Executor -> Tool Caller pipeline."""

    def __init__(self, model: object, history: ConversationHistory, game_state: object, thoughts_container: object, k=5):
        self.model = model
        self.history = history
        self.game_state = game_state
        self.thoughts_container = thoughts_container
        self.k = k

        # Initialize all agents
        agents = {
            "WorldCreatorAgent": WorldCreatorAgent(model, k=self.k),
            "StoryTellerAgent": StoryTellerAgent(model, k=self.k),
            "NarrativeAgent": NarrativeAgent(model, k=self.k),
            "PlannerAgent": PlannerAgent(model, k=self.k),
            "ExecutorAgent": ExecutorAgent(model, k=self.k),
            "ToolCallerAgent": ToolCallerAgent(model, k=self.k),
            "GreetingAgent": GreetingAgent(model, k=self.k),
        }

        # Set history for all agents that require it
        for agent in agents.values():
            if hasattr(agent, 'set_history'):
                agent.set_history(history)

        self.agents = agents

        # Define the tools available for the Planner and Executor.
        # Note: NarrativeAgent, PlannerAgent, ExecutorAgent, and ToolCallerAgent are internal and not exposed as callable tools.
        self.tools = {
            name: {
                "agent": agent,
                "briefing": agent.get_briefing()
            }
            for name, agent in agents.items()
            if name in ["WorldCreatorAgent", "StoryTellerAgent"] # try to remove "GreetingAgent"
            # if name in ["WorldCreatorAgent", "StoryTellerAgent", "GreetingAgent"] 
        }

        # Add workflows to the list of available tools for the planner
        character_creation_workflow = CharacterCreationWorkflow(model, history, self.game_state, self.thoughts_container, k=self.k)
        self.tools["CharacterCreationWorkflow"] = {
            "agent": character_creation_workflow,
            "briefing": character_creation_workflow.get_briefing()
        }

    def _get_stream_writer(self, container):
        """Returns a function that can write to a Streamlit container."""
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
        """Extracts and repairs a JSON object from a string."""
        # Regex to find a JSON block, even with missing closing braces
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*)', text, re.DOTALL) # Fallback for raw JSON
        
        if json_match:
            json_str = json_match.group(1)
            try:
                # Use json_repair to fix common syntax errors
                return json.loads(repair_json(json_str))
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse JSON: {e}\nRaw string: {json_str}")
                return None
        return None

    def get_briefing(self) -> str:
        return "Manages the entire game flow by orchestrating a sequence of specialized agents (Planner, Executor, Tool Caller) to interpret user input, form a plan, and generate a narrative response."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "player_input": {"type": "string", "description": "The latest input from the user to drive the game forward."}
            },
            "required": ["player_input"]
        }'''



    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        player_input = parameters.get("player_input")
        """Runs the new Planner -> Executor -> Tool Caller workflow."""
        # Use the provided stream_callback, or create a default one from the container if none is given.
        sidebar_writer = stream_callback if stream_callback else self._get_stream_writer(self.thoughts_container)
        available_tools_for_planner = [
            {"name": name, "briefing": data["briefing"]}
            for name, data in self.tools.items()
        ]
        
        main_memory = [f"User's initial request: {player_input}"]
        max_turns = 10

        for i in range(max_turns):
            sidebar_writer(f"\n--- **Loop {i+1} / {max_turns}** ---\n")

            # 1. Planner Agent: Creates a high-level plan using the main memory.
            logging.info(f"Calling PlannerAgent with scratchpad: {'\n'.join(main_memory)}")
            planner_params = {
                "available_tools": available_tools_for_planner,
                "scratchpad": "\n".join(main_memory),
                "current_turn": i + 1,
                "max_turns": max_turns
            }
            plan_text = self.agents["PlannerAgent"].execute_with_parameters(
                parameters=planner_params,
                stream_callback=sidebar_writer # Pass the correct writer
            )
            main_memory.append(f"**Planner's Plan:**\n{plan_text}")

            # 2. Executor Agent: Decides the next action based on the plan and main memory.
            logging.info(f"Calling ExecutorAgent with planner_output: {plan_text}")
            executor_params = {
                "planner_output": plan_text,
                "scratchpad": "\n".join(main_memory),
                "available_tools": available_tools_for_planner
            }
            executor_output = self.agents["ExecutorAgent"].execute_with_parameters(
                parameters=executor_params,
                stream_callback=sidebar_writer # Pass the correct writer
            )
            # NOTE: executor_output is NOT added to main_memory here. It's part of the temporary memory for the tool caller.

            # 3. Parse Executor's JSON command
            executor_command = self._extract_json(executor_output)
            if not executor_command or "current_execution" not in executor_command:
                sidebar_writer("**Error:** Executor failed to produce a valid command. Aborting.")
                break

            execution_status = executor_command.get("current_execution")
            tool_name = executor_command.get("tool_name")

            sidebar_writer(f"\n**Executor's Action:** `{execution_status}`")
            if tool_name:
                sidebar_writer(f" on Tool: `{tool_name}`")
            sidebar_writer("\n")

            # 4. Handle Executor's decision
            if execution_status in ["task_complete", "ask_for_user_input"]:
                # Add Executor's action to main memory in this branch since it's the final decision, executor_output is important in the last round especially when it conflicts the planner
                main_memory.append(f"**Executor's Action:**\n{executor_output}")
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

                # 5. Check if the tool requires parameters
                try:
                    params_schema_str = target_tool.get_required_parameters()
                    params_schema = json.loads(repair_json(params_schema_str))
                    required_params = params_schema.get("required", [])
                except (json.JSONDecodeError, ValueError) as e:
                    sidebar_writer(f"**Error:** Could not parse parameters schema for `{tool_name}`: {e}")
                    break

                filled_params = {}
                # If parameters are required, call the ToolCallerAgent
                if required_params:
                    # Create temporary memory for the Tool Caller
                    temporary_memory = main_memory + [f"**Executor's Decision:**\n{executor_output}"]
                    
                    logging.info(f"Calling ToolCallerAgent for tool: {tool_name}")
                    tool_caller_params = {
                        "scratchpad": "\n".join(temporary_memory),
                        "tool_to_call": tool_name,
                        "tool_params_schema": params_schema_str
                    }
                    tool_caller_output = self.agents["ToolCallerAgent"].execute_with_parameters(
                        parameters=tool_caller_params,
                        stream_callback=sidebar_writer # Pass the correct writer
                    )

                    # Parse Tool Caller's JSON
                    filled_params = self._extract_json(tool_caller_output)
                    if filled_params is None:
                        sidebar_writer(f"**Error:** Tool Caller failed to produce valid JSON for `{tool_name}`. Aborting.")
                        break

                    # Special handling for CharacterCreationWorkflow, but let's remove it and let the workflow handle it
                    # if tool_name == "CharacterCreationWorkflow":
                    #     if "creation_guidance" in params_schema.get("properties", {}):
                    #         # Use the original player_input as the creation_guidance
                    #         filled_params["creation_guidance"] = player_input

                    # Always add the thoughts container if the target tool accepts it
                    # The thoughts_container is now part of the workflow's state, so we don't need to pass it.
                    
                    main_memory.append(f"**Parameters for `{tool_name}`:**\n```json\n{json.dumps(filled_params, indent=2)}\n```")
                else:
                    sidebar_writer(f"**Info:** Tool `{tool_name}` requires no parameters. Executing directly.\n")

                sidebar_writer(f"\n**Action:** Calling `{tool_name}` with params: `{json.dumps(filled_params)}`\n")

                # 6. Execute the tool and add the result to main memory
                try:
                    # This assumes the tool's execute method matches the parameters
                    tool_result = target_tool.execute_with_parameters(
                        parameters=filled_params,
                        stream_callback=sidebar_writer # Pass the correct writer
                    )
                    if tool_result:
                        main_memory.append(f"**Result from `{tool_name}`:**\n{tool_result}")
                    sidebar_writer(f"**Success:** `{tool_name}` executed successfully.\n")
                except Exception as e:
                    error_message = f"**Error:** Failed to execute tool `{tool_name}`: {e}"
                    main_memory.append(error_message)
                    sidebar_writer(f"{error_message}\n")
                    break # Stop the loop on tool execution failure
            else:
                sidebar_writer(f"**Error:** Unknown execution status: `{execution_status}`. Aborting.")
                break

        if i == max_turns - 1:
            sidebar_writer("**Warning:** Reached maximum loop limit.")

        sidebar_writer("\n**Info:** Planning loop finished. Generating final narrative response.\n")
        final_scratchpad = "\n".join(main_memory)
        
        logging.info(f"Calling NarrativeAgent with final scratchpad: {final_scratchpad}")
        narrative_params = {
            "narrative_context": final_scratchpad
        }
        # Unlike other agents that return a complete string, NarrativeAgent is special.
        # It overrides its execution method to use 'yield', creating a generator.
        # This is done specifically to stream its output chunk by chunk to the main UI,
        # allowing the user to see the final story unfold in real-time.
        # Therefore, this variable holds a generator, not a string.
        final_response_generator = self.agents["NarrativeAgent"].execute_with_parameters(
            parameters=narrative_params
        )
        # The generator is returned for completeness, but the streaming is handled by the callback.
        return final_response_generator