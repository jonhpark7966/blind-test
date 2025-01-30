# utils/share_link_generator.py

import streamlit as st

def generate_shareable_link(contest_id: str) -> str:
    """Generates a shareable link including the session ID."""
    base_url = st.secrets["base_url"]  # Assuming you have a base URL in your secrets
    session_id = st.session_state.get('session_id')
    if not session_id:
        raise ValueError("Session ID is not available in session state.")
    
    shareable_link = f"{base_url}/?contest_id={contest_id}&session_id={session_id}"
    return shareable_link