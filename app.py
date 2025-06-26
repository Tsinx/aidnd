import streamlit as st
import logging
from dnd_game.workflow import GameWorkflow
from dnd_game.history import ConversationHistory
from dnd_game.game_engine.game_state import GameState
from dnd_game.game_engine.character import Character
from utils import load_model

st.set_page_config(layout="wide")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

st.title("D&D AI Dungeon Master")

# --- Session State Initialization ---
# --- Session State Initialization ---
def initialize_session_state():
    if 'llm' not in st.session_state:
        try:
            llm = load_model()
            st.session_state.llm = llm
            st.session_state.model = llm
            st.session_state.history = ConversationHistory(st.session_state.llm, k=5)
            if 'game_state' not in st.session_state:
                st.session_state.game_state = GameState()
            st.sidebar.title("DM's Brain")
            st.sidebar.markdown("### Story Summary")
            summary_text = st.session_state.history.get_latest_summary()
            st.sidebar.markdown(f"""> {summary_text.replace('\n', '\n> ')}
""")
            st.sidebar.markdown("### High-Level Summary")
            super_summary_text = st.session_state.history.get_latest_super_summary()
            st.sidebar.markdown(f"""> {super_summary_text.replace('\n', '\n> ')}""")
            st.sidebar.markdown("---")
            thoughts_container = st.sidebar.container()
            thoughts_container.write("The inner workings of the agents will appear here...")
            st.session_state.thoughts_container = thoughts_container

            st.session_state.game_workflow = GameWorkflow(model=st.session_state.model, history=st.session_state.history, game_state=st.session_state.game_state, thoughts_container=st.session_state.thoughts_container, k=5)
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.game_state.characters:
        game_state = st.session_state.game_state
        player = Character(name="Player", description="A brave adventurer", background="Mysterious", character_class="Warrior", level=1, max_hp=100, max_mp=20, strength=15, dexterity=12, stamina=14, intelligence=10, willpower=11, bloodline=0, is_player=True)
        npc1 = Character(name="Elora", description="A wise elf", background="Noble", character_class="Mage", level=5, max_hp=80, max_mp=50, strength=8, dexterity=14, stamina=10, intelligence=18, willpower=15, bloodline=0, is_player=False)
        npc2 = Character(name="Grom", description="A strong orc", background="Outcast", character_class="Barbarian", level=3, max_hp=120, max_mp=10, strength=18, dexterity=10, stamina=16, intelligence=8, willpower=9, bloodline=0, is_player=False)
        game_state.add_character(player)
        game_state.add_character(npc1)
        game_state.add_character(npc2)

initialize_session_state()



# --- Main Chat Interface ---
# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What do you do?"):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.history.add_user_input(prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Clear sidebar and process the turn
    st.session_state.thoughts_container.empty()
    with st.chat_message("assistant"):
        # This is where the magic happens. We execute the workflow and stream the output.
        params = {
            "player_input": prompt
        }
        response_generator = st.session_state.game_workflow.execute_with_parameters(parameters=params)
        full_response = st.write_stream(response_generator)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.history.add_ai_response(full_response)

    # Note: Summarization is now implicitly part of the StoryTellerAgent's context
    # and doesn't need to be a separate, visible step here.
    # A more advanced implementation could add a summarization agent to the workflow.