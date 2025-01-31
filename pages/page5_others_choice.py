import streamlit as st
import pandas as pd
import os
from utils.contest_sidebar import display_contest_sidebar, load_contest_df
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.metadata_handler import MetadataHandler, get_metadata_handler

def display_match_stats(metadata_handler: MetadataHandler, stats_handler: StatsHandler, match_number: int):
    """Display the statistics and results of a match visually."""
    match_data = metadata_handler.get_matches()
    
    st.write(f"### Match {match_number}")
    
    # Load statistics data
    stats = pd.read_csv(stats_handler.stats_path)
    vote_stats = pd.read_json(stats['vote_percentage'].iloc[0])
    match_stats = vote_stats['match_number'][str(match_number)]
    
    # Calculate total votes for the match
    total_votes = sum(match_stats.values())
    
    # Determine the most voted option
    most_voted = max(match_stats.items(), key=lambda x: x[1])[0]
    
    # Display images/videos with statistics
    col1, col2 = st.columns(2)
    for data in match_data:
        filename = data['filename']
        option = data['option']
        model = data.get('model', '')
        votes = match_stats.get(option, 0)
        vote_percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        
        # Determine border color
        border_color = "green" if votes > total_votes / 2 else "gray"
        
        with col1 if option == match_data[0]['option'] else col2:
            if filename.lower().endswith(('.mp4', '.mov')):
                st.video(os.path.join(metadata_handler.contest_dir, filename))
            else:
                st.image(os.path.join(metadata_handler.contest_dir, filename))
            st.write(f"Model: {model}")
            st.markdown(
                f"<div style='border:2px solid {border_color};padding:10px'>"
                f"Option: {option}<br>"
                f"Votes: {votes} ({vote_percentage:.1f}%)"
                f"</div>",
                unsafe_allow_html=True
            )

def main():
    st.title("Detailed Voting Results")

    # Initialize session
    SessionManager.init_session()

    # 컨테스트 선택
    contest = display_contest_sidebar()
    metadata_handler = get_metadata_handler(contest['dir_path'])
    stats_handler = StatsHandler(contest['dir_path'])
    
    # Load all matches
    match_data = metadata_handler.get_matches()
    # match_data is list of dictionary, 
    # get sorted unique match numbers
    match_numbers = sorted(set(item['Match'] for item in match_data))
    
    # load all 
    # Display each match with statistics
    for match_number in match_numbers:
       display_match_stats(metadata_handler, stats_handler, match_number)
    
    # Back button
    if st.button("Back to Statistics"):
        st.switch_page("pages/page3_stats.py")

if __name__ == "__main__":
    main() 