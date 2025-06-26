import streamlit as st
import llama_cpp
from llama_cpp import Llama

@st.cache_resource
def load_model():
    """Loads the GGUF model using llama-cpp-python."""
    # This is a placeholder path. You need to download the GGUF model file
    # and place it in your project directory, then update this path.
    model_path = "/mnt/gemma-3-27b-it-abliterated.q6_k.gguf"

    try:
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,  # Offload all layers to GPU
            n_ctx=56000,       # Context window size
            verbose=False,     # Set to True for debugging
            type_k=8,  # Use Q8_0 for KV cache, as it's supported by Flash Attention
            type_v=8,  # Use Q8_0 for KV cache, as it's supported by Flash Attention
            flash_attn=True   # Enable Flash Attention
        )
        # Return the model instance. No tokenizer is needed separately for llama-cpp.
        return llm
    except Exception as e:
        # Provide a more helpful error message if the model file is not found.
        print(f"Error loading model: {e}")
        print(f"Please make sure you have downloaded a GGUF model file and updated the 'model_path' in utils.py to point to it.")
        return None