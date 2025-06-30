# AI Dungeon Master for D&D

This project is a text-based Dungeons & Dragons (D&D) game that uses a Large Language Model (LLM) to act as the Dungeon Master (DM). It provides an interactive and dynamic storytelling experience where the player's decisions shape the narrative.

## Current Features

*   **Interactive Storytelling**: The AI DM generates dynamic and engaging narratives based on player input.
*   **Character Management**: The game manages player and non-player characters (NPCs), including their stats and attributes.
*   **Conversation History**: The game maintains a history of the conversation, allowing the AI to have context-aware responses.
*   **Modular Agent-based Architecture**: The AI is built with a system of specialized agents (e.g., Narrative Agent, Planner Agent, Story Teller Agent) that work together to create a coherent and engaging story.
*   **Web-based UI**: The game is played through a user-friendly web interface built with Streamlit.

## Future Plans

*   **Advanced Character Creation**: A more detailed character creation process, allowing players to customize their characters further.
*   **Inventory and Item Management**: The ability for players to acquire, use, and manage items.
*   **Faction and Reputation System**: A system to track the player's relationships with different factions in the game world.
*   **Multiplayer Support**: Allow multiple players to join the same game session.
*   **Enhanced AI**: Improve the AI's ability to remember long-term plot points and maintain a consistent world state.

## Project Highlights

*   **Powered by LLMs**: Leverages the power of large language models to create a unique and replayable D&D experience.
*   **Extensible Framework**: The modular design allows for easy expansion with new agents, tools, and game mechanics.
*   **Focus on Narrative**: The project prioritizes immersive storytelling and player agency.

## How to Use

1.  **Install Dependencies**: Make sure you have Python 3 installed. Then, install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up Environment**: You will need to configure your LLM provider and API key. This project uses a `utils.py` file to load the model, which you may need to adapt for your specific setup.

3.  **Run the Application**:

    ```bash
    python run.py
    ```

4.  **Open in Browser**: The application will be available at a local URL (usually `http://localhost:8501`). Open this URL in your web browser to start playing.