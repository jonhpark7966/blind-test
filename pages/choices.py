import streamlit as st
import pandas as pd
import os
from utils.contest_sidebar import display_contest_sidebar, load_contest_df
from utils.media_handler import display_media, load_media
from utils.session_manager import SessionManager
from utils.metadata_handler import MetadataHandler, get_metadata_handler
from utils.tag_styler import display_tags
from utils.votes_handler import load_my_votes, load_shared_votes
from utils.match_display import display_match_result, display_pagination


def main():
    st.title("선택 돌아보기")
    
    # Initialize session
    SessionManager.init_session()

    is_shared = False
    try:
        contest_id = st.query_params["contest_id"]
        session_id = st.query_params["session_id"]

        if session_id != st.session_state.get('session_id'):
            is_shared = True

    except Exception as e:
        # there are no get params. goes to my rexults.
        contest_id = st.session_state.get('last_contest_id')
        session_id = st.session_state.get('session_id')
        st.query_params['session_id'] = st.session_state.get('session_id')

    contest = display_contest_sidebar(contest_id)
    st.query_params['contest_id'] = str(contest['contest_id'])

    metadata_handler = get_metadata_handler(contest['dir_path'])
    
    # Load my vote results
    if is_shared:
        print(contest_id, session_id)
        my_votes = load_shared_votes(str(contest['contest_id']), session_id)
    else:
        my_votes = load_my_votes(contest['dir_path'])

    print(my_votes) 
    if not my_votes:
        st.write("아직 투표 결과가 없습니다.")
        if st.button("투표 하러가기"):
            st.switch_page("pages/vote.py")
        return

    if is_shared:
        if st.button("나도 투표하러 가기"):
            st.switch_page("pages/vote.py")
    
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
    display_pagination(total_pages)


if __name__ == "__main__":
    main() 