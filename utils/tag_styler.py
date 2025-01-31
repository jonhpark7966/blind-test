import random
import streamlit as st

def display_tags(tags):
    """Display tags with styled HTML in Streamlit."""
    if tags:
        tag_style_template = (
            "display: inline-block; border: 2px solid {color}; color: {color}; "
            "padding: 8px 15px; margin: 5px; border-radius: 20px; font-size: 16px;"
            "background-color: transparent;"
        )
        pastel_colors = ["#FFB6C1", "#FFD1DC", "#FFC0CB", "#FFCCEB"]  # examples
        styled_tags = [
            f"<span style='{tag_style_template.format(color=random.choice(pastel_colors))}'>{tag}</span>"
            for tag in tags
        ]
        st.markdown(" ".join(styled_tags), unsafe_allow_html=True) 