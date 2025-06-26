from .agents.base import BaseAgent

class SummarizerAgent(BaseAgent):
    """An agent that summarizes the conversation."""
    def get_briefing(self) -> str:
        return "An agent that summarizes the conversation."

    def get_required_parameters(self) -> str:
        return '{"type": "object", "properties": {"previous_summary": {"type": "string"}, "new_lines": {"type": "string"}}, "required": ["previous_summary", "new_lines"]}'

    def execute(self, previous_summary: str, new_lines: str) -> str:
        prompt = f"""Your task is to summarize a turn of a Dungeons & Dragons game session. You will be given the previous summary and the latest turn of dialogue. Condense the new dialogue into a single, concise bullet point that captures the most important actions, decisions, or revelations. Return only the new bullet point.

Previous Summary:
{previous_summary}

New Lines of Dialogue:
{new_lines}

New Summary Point:"""
        return self._generate_response(prompt)

class SuperSummarizerAgent(BaseAgent):
    """An agent that creates a high-level summary from recent summary points."""
    def get_briefing(self) -> str:
        return "An agent that creates a high-level summary from recent summary points."

    def get_required_parameters(self) -> str:
        return '{"type": "object", "properties": {"previous_super_summary": {"type": "string"}, "recent_summaries": {"type": "string"}}, "required": ["previous_super_summary", "recent_summaries"]}'

    def execute(self, previous_super_summary: str, recent_summaries: str) -> str:
        prompt = f"""Your task is to create a high-level summary of a Dungeons & Dragons game session. You will be given the previous high-level summary for context, and a list of the 10 most recent events. Your goal is to condense the recent events into a single, new, concise paragraph that captures the overarching narrative progress. Return ONLY the new summary paragraph, do not include the previous summary.

Previous High-Level Summary (for context):
{previous_super_summary}

Recent Events:
{recent_summaries}

New High-Level Summary Paragraph:"""
        return self._generate_response(prompt)


class ConversationHistory:
    SUPER_SUMMARY_INTERVAL = 10
    """
    Manages the conversation history and generates a running summary.
    """
    def __init__(self, model, k=5):
        self.turns = []
        self.summaries = ["The story has not yet begun."]
        self.summarizer_agent = SummarizerAgent(model, k=k)
        self.super_summaries = ["The overall story has not yet begun."]
        self.super_summarizer_agent = SuperSummarizerAgent(model, k=k)

    def add_user_input(self, user_input):
        """Adds the user's part of a new turn to the history."""
        # Ensure the last turn is complete before adding a new one
        if self.turns and self.turns[-1]["ai_response"] is None:
            # This case might indicate a logic error, where a new user input
            # is added before the AI has responded to the previous one.
            # For now, we'll log a warning or handle it as needed.
            # For simplicity, we'll just overwrite the last user input.
            self.turns[-1]["user_input"] = user_input
        else:
            turn = {
                "user_input": user_input,
                "ai_response": None
            }
            self.turns.append(turn)

            # Add placeholder for the summary
            if len(self.summaries) == 1 and self.summaries[0] == "The story has not yet begun.":
                self.summaries[0] = "[PENDING AI RESPONSE...]"
            else:
                self.summaries.append("[PENDING AI RESPONSE...]")

            # Check if a super summary placeholder is also needed
            if len(self.summaries) > 1 and (len(self.summaries) - 2) % self.SUPER_SUMMARY_INTERVAL == 0:
                self.super_summaries.append("[PENDING AI RESPONSE...]")

    def add_ai_response(self, ai_response):
        """Adds the AI's part of the current turn and triggers summarization."""
        if not self.turns or self.turns[-1]["ai_response"] is not None:
            # This indicates an attempt to add an AI response without a preceding user input.
            # Or the turn is already complete. Handle as an error or ignore.
            return

        # Complete the turn
        self.turns[-1]["ai_response"] = ai_response
        latest_turn = self.turns[-1]

        # Update summary
        new_lines = f"Player: {latest_turn['user_input']}\nDM: {ai_response}"
        # Exclude the placeholder from the context for the summarizer
        previous_summary_for_agent = "\n".join(self.summaries[:-1])
        new_summary_point = self.summarizer_agent.execute(
            previous_summary=previous_summary_for_agent,
            new_lines=new_lines
        ).strip()

        # Replace the placeholder with the actual summary
        self.summaries[-1] = new_summary_point

        # Update super summary if needed
        # Update super summary if its placeholder was added
        if len(self.summaries) > 1 and (len(self.summaries) - 1) % self.SUPER_SUMMARY_INTERVAL == 0:
            # The placeholder for super_summary was added in add_user_input
            # We now generate the real summary and replace the placeholder
            recent_summaries_text = "\n".join(self.summaries[-self.SUPER_SUMMARY_INTERVAL:])
            # Get the summary before the placeholder was added
            previous_super_summary = "\n".join(self.super_summaries[:-1])

            new_super_summary_paragraph = self.super_summarizer_agent.execute(
                previous_super_summary=previous_super_summary,
                recent_summaries=recent_summaries_text
            ).strip()

            # Replace the placeholder
            self.super_summaries[-1] = new_super_summary_paragraph

    def get_history(self, k=1):
        if not self.turns:
            return "This is the first turn of the conversation.", ""

        # The latest turn is always separate
        latest_turn_index = len(self.turns) - 1
        latest_turn = self.turns[latest_turn_index]
        if latest_turn['ai_response'] is None:
            latest_turn_str = f"step {latest_turn_index}: user: {latest_turn['user_input']}"
        else:
            latest_turn_str = f"step {latest_turn_index}: user: {latest_turn['user_input']} respond: {latest_turn['ai_response']}"

        if len(self.turns) == 1:
            return latest_turn_str, "This is the first turn of the conversation."

        # The rest of the history to be constructed
        history_parts = []
        history_end_index = latest_turn_index # We build history up to the turn before the latest

        # Detailed history (last k turns, excluding the latest)
        detailed_start_index = max(0, history_end_index - k)
        
        # Iterate backwards from the turn before the latest
        current_pos = history_end_index - 1
        while current_pos >= 0:
            # Decide what to add: detailed turn, summary, or super summary
            if current_pos >= detailed_start_index:
                # Add detailed turn
                turn = self.turns[current_pos]
                history_parts.insert(0, f"step {current_pos}: user: {turn['user_input']} respond: {turn['ai_response']}")
                current_pos -= 1
            elif (current_pos + 1) % self.SUPER_SUMMARY_INTERVAL == 0:
                # Add super summary for a block of 10
                # The block index for super_summaries is based on which block of 10 we are in.
                super_summary_block_index = (current_pos) // self.SUPER_SUMMARY_INTERVAL
                start = super_summary_block_index * self.SUPER_SUMMARY_INTERVAL
                end = start + 9
                super_summary_text = self.super_summaries[super_summary_block_index] if super_summary_block_index < len(self.super_summaries) else "Summary not available"
                history_parts.insert(0, f"step {start}-{end}: {super_summary_text}")
                current_pos = start - 1 # Move to the position before this block
            else:
                # Add individual summary
                summary_text = self.summaries[current_pos] if current_pos < len(self.summaries) else "Summary not available"
                history_parts.insert(0, f"step {current_pos}: {summary_text}")
                current_pos -= 1

        past_history_str = "\n".join(history_parts)
        return latest_turn_str, past_history_str

    def get_latest_summary(self):
        """Returns the current summary of the conversation."""
        return "\n".join(self.summaries)

    def get_latest_super_summary(self):
        """Returns the latest super summary."""
        return self.super_summaries[-1]

    def format_for_llm(self):
        """Formats the history into a string suitable for LLM context."""
        formatted_history = []
        for turn in self.turns:
            formatted_history.append(f"Player: {turn['user_input']}")
            formatted_history.append(f"DM: {turn['ai_response']}")
        return "\n".join(formatted_history)