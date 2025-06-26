import os

# This script runs the Streamlit application.
# It is a convenience script to avoid typing the full command in the terminal.

def run_app():
    """
    Runs the streamlit app.
    """
    os.system("streamlit run app.py > app.log 2>&1")

if __name__ == "__main__":
    run_app()