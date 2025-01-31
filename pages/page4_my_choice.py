import streamlit as st
import pandas as pd
import os
from utils.contest_sidebar import load_contest_df
from utils.session_manager import SessionManager
from utils.metadata_handler import MetadataHandler, get_metadata_handler

def display_match_result(metadata_handler: MetadataHandler, match_number: int, chosen_option: str):
    """Display the result of a match visually."""
    match_data = metadata_handler.get_match_metadata(match_number)
    
    st.write(f"### Match {match_number}")
    
    # Display tags
    if match_data and 'tags' in match_data[0]:
        st.write("Tags:", ", ".join(eval(match_data[0]['tags'])))
    
    # Display images/videos
    for data in match_data:
        filename = data['filename']
        option = data['option']
        model = data.get('model', '')
        tags = data.get('tags', '')
        
        # File path
        file_path = os.path.join(metadata_handler.contest_dir, filename)
        
        # Border style based on selection
        border_color = "green" if option == chosen_option else "gray"
        
        # Display model and tags
        st.write(f"Model: {model}")
        
        # Display media with border
        if filename.lower().endswith(('.mp4', '.mov')):
            st.video(file_path)
        else:
            st.image(file_path)
        st.markdown(f"<div style='border:2px solid {border_color};padding:10px'>Selected: {option}</div>", 
                   unsafe_allow_html=True)

def main():
    st.title("Review My Choices")
    
    # Initialize session
    SessionManager.init_session()

    if 'votes' in st.session_state and len(st.session_state.votes) > 0:
        SessionManager.save_votes_and_reset()
    
    # Load contest list
    contests_df = load_contest_df()
    
    # Select contest
    selected_contest = st.selectbox(
        "Select Contest",
        contests_df['contest_name'].tolist()
    )
    
    contest = contests_df[contests_df['contest_name'] == selected_contest].iloc[0]
    metadata_handler = get_metadata_handler(contest['dir_path'])
    
    # Load my vote results
    my_votes = [v for v in SessionManager.get_votes() 
                if v['contest_id'] == contest['contest_id']]
    
    if not my_votes:
        st.write("No voting results for this contest.")
        if st.button("Go to Vote"):
            st.switch_page("pages/page1_vote.py")
        return
    
    # Display results for each match
    for vote in my_votes:
        display_match_result(metadata_handler, vote['match_number'], vote['chosen_option'])

if __name__ == "__main__":
    main() 