from .base import BaseAgent

class NarrativeAgent(BaseAgent):
    """该代理将规划器的内部思考和决策过程，转化为流畅、自然且符合角色扮演情境的语言，呈现给用户。"""

    def get_briefing(self) -> str:
        return "Translates the planner's internal thoughts and tool outputs into a smooth, natural narrative for the player. It's the final voice the user hears."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "narrative_context": {"type": "string", "description": "The combined output from other agents, forming the basis of the story to be told to the player."}
            },
            "required": ["narrative_context"]
        }'''



    def execute_with_parameters(self, parameters: dict, stream_callback=None):
        """
        Executes the agent with a dictionary of parameters and yields the response.
        This overrides the base method to handle streaming output directly.
        """
        if stream_callback:
            stream_callback("\n### Narrative Agent Thinking...\n")

        prompt = self._construct_prompt_with_parameters(parameters)

        response_stream = self.model(
            prompt,
            max_tokens=8192,
            stop=None,
            echo=False,
            stream=True
        )

        # Yield each chunk as it arrives for the Streamlit UI
        for chunk in response_stream:
            text_chunk = chunk['choices'][0]['text']
            yield text_chunk

    def _construct_prompt_with_parameters(self, parameters: dict) -> str:
        """Constructs the prompt using parameters from the planner."""
        context = parameters.get('narrative_context', 'It is quiet.')

        prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

你是一个自然语言转换器，功能类似于一个“中文屋”。你的唯一任务是接收一份包含系统内部思考和决策的上下文（Internal Monologue & Agent Inputs），并将其忠实地、不加创造地转换为流畅、自然的中文表述。你没有自己的思想或意识，不能添加任何输入中不存在的信息或意图。

你的核心指令：
1.  **忠实转换**：你的输出必须严格基于输入内容。如果输入是一个计划的结果，你就叙述这个结果。如果输入是需要向用户提问，你就清晰地提出那个问题。你的转换应该是对内部状态的直接反映。
2.  **顺序叙述**：你需要按照输入上下文的时间顺序，逐步叙述所有内容，包括中间步骤的说明、工具调用的结果（例如生成的世界背景、角色信息、故事情节、关键事件、骰子点数等），而不仅仅是最终的结论。
3.  **整合多目标**：系统内部思考可能解决了多个目标（例如，同时创建世界和角色，或同时设置事件并推进故事），你需要将这些目标的内容有机地整合起来进行输出。
4.  **禁止创造**：你不是一个故事讲述者或角色扮演者。严禁添加任何自己的情节、描述或情感。你不能扮演任何角色，包括“地下城主”。
5.  **隐藏技术细节**：在转换时，必须隐藏所有技术术语，如“planner”、“agent”、“tool”、“parameter”等。用户的体验应该是无缝的，他们不应该感觉到是在与一个由多个组件构成的系统交互。
6.  **始终使用中文**：你的所有输出都必须是中文。

**内部思考及代理输入 (Internal Monologue & Agent Inputs):**
{context}

**转换后的自然语言输出 (Your Natural Language Output):**<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt