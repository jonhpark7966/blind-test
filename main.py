import streamlit as st
import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="블라인드 테스트",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state if needed
if "votes" not in st.session_state:
    st.session_state.votes = []

# Redirect to page1_votes
st.switch_page("pages/page1_votes.py") 