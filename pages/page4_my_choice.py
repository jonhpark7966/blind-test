import streamlit as st
import pandas as pd
import os
from utils.contest_sidebar import display_contest_sidebar, load_contest_df
from utils.media_handler import display_media, load_media
from utils.session_manager import SessionManager
from utils.metadata_handler import MetadataHandler, get_metadata_handler
from utils.votes_handler import load_my_votes

def display_match_result(metadata_handler: MetadataHandler, match_number: int, chosen_option: str, index: int):
    """Display the result of a match visually."""
    match_data = metadata_handler.get_matches()

    # Display images/videos
    border_colors = []
    medias = []
    models = []
    for data in match_data:
        # filter by match number 
        if data['Match'] != match_number:
            continue

        filename = data['FileName']
        model = data.get('Model', '')
        tags = data.get('tag', '')

        # File path
        file_path = os.path.join(metadata_handler.directory, filename)

        # Border style based on selection
        border_colors.append("green" if filename == chosen_option else "gray")
        models.append(model)
        medias.append(load_media(file_path, metadata_handler))

    with st.container():
        # view match number and tags    
        st.write(f"### Match {index}")
        st.write(f"Tags: {tags}")
        col1, col2 = st.columns(2)

        # Determine which media should be in col1 based on selection
        if border_colors[0] == "green":
            first_media_index = 0
            second_media_index = 1
        else:
            first_media_index = 1
            second_media_index = 0

        with col1:
            # show model name and media with border color
            border_width = "3px"  # Increase border width
            check_icon = "✅" if border_colors[first_media_index] == "green" else ""
            st.markdown(f"<div style='border: {border_width} solid {border_colors[first_media_index]}; padding: 10px;'>"
                        f"<div style='color: {border_colors[first_media_index]};'>{models[first_media_index]} {check_icon}</div>", unsafe_allow_html=True)
            display_media(col1, medias[first_media_index])

        with col2:
            # show model name and media with border color
            border_width = "3px"  # Increase border width
            check_icon = "✅" if border_colors[second_media_index] == "green" else ""
            st.markdown(f"<div style='border: {border_width} solid {border_colors[second_media_index]}; padding: 10px;'>"
                        f"<div style='color: {border_colors[second_media_index]};'>{models[second_media_index]} {check_icon}</div>", unsafe_allow_html=True)
            display_media(col2, medias[second_media_index])


def main():
    st.title("Review My Choices")
    
    # Initialize session
    SessionManager.init_session()

    # 컨테스트 선택
    contest = display_contest_sidebar()
    metadata_handler = get_metadata_handler(contest['dir_path'])
    
    # Load my vote results
    my_votes = load_my_votes(contest['dir_path'])
    
    if not my_votes:
        st.write("No voting results for this contest.")
        if st.button("Go to Vote"):
            st.switch_page("pages/page1_vote.py")
        return
    
    # Initialize page number in session state if not already set
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

    # Display results for each match with pagination
    page_size = 5  # Number of matches to display per page
    total_matches = len(my_votes)
    total_pages = (total_matches // page_size) + (1 if total_matches % page_size > 0 else 0)

    start_index = (st.session_state.page_number - 1) * page_size
    end_index = start_index + page_size

    # Display matches for the current page
    for i, vote in enumerate(my_votes[start_index:end_index]):
        index = start_index + i + 1
        display_match_result(metadata_handler, vote['match_number'], vote['chosen_option'], index)


    # Pagination controls
    col1, col2, col3 = st.columns(3, gap="large")
    

    def prev_page():
        if st.session_state.page_number > 1:
            st.session_state.page_number -= 1

    def next_page():
        if st.session_state.page_number < total_pages:
            st.session_state.page_number += 1

    with col1:
        st.button("⬅", on_click=prev_page, use_container_width=True)

    with col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 20px;'>"
            f"Page {st.session_state.page_number} of {total_pages}"
            f"</div>",
            unsafe_allow_html=True)

    with col3:
        st.button("➡", on_click=next_page, use_container_width=True)


if __name__ == "__main__":
    main() 