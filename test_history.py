import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dnd_game.history import ConversationHistory
from utils import load_model

def run_test():
    """Runs a test of the ConversationHistory class."""
    print("--- Initializing Test ---")
    llm = load_model()
    if llm is None:
        print("ERROR: Failed to load model. Aborting test.")
        return

    history = ConversationHistory(model=llm)
    print("ConversationHistory initialized.")

    # Simulated conversation
    simulated_conversation = [
        ("I want to create a character, a sneaky rogue.", "A fine choice! What is your character's name?"),
        ("Let's call him 'Whisper'.", "Excellent. Whisper, the sneaky rogue. Where does his story begin? In a bustling city or a remote village?"),
        ("He starts in a dark alley in a port city.", "The scent of salt and tar fills the air. As Whisper lurks in the shadows, he overhears a plot. What does he do?"),
        ("He decides to follow the conspirators.", "He tails them to a warehouse. Inside, a deal is being struck over a mysterious glowing artifact."),
        ("He tries to steal the artifact.", "With nimble fingers, he snatches the artifact! An alarm blares. He must escape!"),
        ("He dashes out a window and onto the rooftops.", "He leaps from roof to roof, the city guard in hot pursuit below."),
        ("He finds a hiding spot.", "He ducks into a chimney, waiting for the guards to pass. The artifact hums in his hand."),
        ("He examines the artifact more closely.", "It glows with an inner light, covered in strange runes. It feels warm to the touch."),
        ("He tries to decipher the runes.", "The runes are ancient, beyond his knowledge. He realizes he needs to find a scholar."),
        ("He seeks out the city's library.", "The library is a vast, dusty place. The librarian, a stern old woman, eyes him suspiciously."),
        ("He asks for books on ancient artifacts.", "She directs him to a forbidden section, warning him of the dangers within. The artifact seems to react to a specific tome."),
    ]

    for i, (user_input, ai_response) in enumerate(simulated_conversation):
        print(f"\n--- Turn {i+1} ---")
        print(f"USER: {user_input}")

        # 1. Add user input
        history.add_user_input(user_input)
        print("\n**After add_user_input:**")
        print(f"Turns: {history.turns}")
        print(f"Summaries: {history.summaries}")
        print(f"Super Summaries: {history.super_summaries}")

        latest, past = history.get_history(k=3)
        print("\n**get_history() output (before AI response):**")
        print(f"  Latest Turn: {latest}")
        print(f"  Past History:\n{past}")

        # 2. Add AI response
        print(f"\nAI: {ai_response}")
        history.add_ai_response(ai_response)
        print("\n**After add_ai_response:**")
        print(f"Turns: {history.turns}")
        print(f"Summaries: {history.summaries}")
        print(f"Super Summaries: {history.super_summaries}")

        latest, past = history.get_history(k=3)
        print("\n**get_history() output (after AI response):**")
        print(f"  Latest Turn: {latest}")
        print(f"  Past History:\n{past}")

        print("\n**Current Summaries:**")
        print(f"  Latest Summary: {history.get_latest_summary()}")
        print(f"  Latest Super Summary: {history.get_latest_super_summary()}")

    print("\n--- Test Finished ---")

if __name__ == "__main__":
    run_test()