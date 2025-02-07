import streamlit as st
import pandas as pd
import os
from utils.contest_sidebar import display_contest_sidebar, load_contest_df
from utils.media_handler import display_media, load_media
from utils.session_manager import SessionManager
from utils.metadata_handler import MetadataHandler, get_metadata_handler
from utils.stats_handler import StatsHandler
from utils.tag_styler import display_tags
from utils.votes_handler import load_my_votes
from utils.match_display import display_match_result, display_pagination, display_total_match_result


def main():
    st.title("다른 사람들의 투표 결과 보기")
    
    # Initialize session
    SessionManager.init_session()

    # 컨테스트 선택
    # 사이드바에 컨테스트 목록 표시
    default_contest_id = st.session_state.get('last_contest_id')
    contest = display_contest_sidebar(default_contest_id)
    metadata_handler = get_metadata_handler(contest['dir_path'])
    
    # Load stats per match
    stats_handler = StatsHandler(contest['dir_path'])
    stats_per_match = stats_handler.load_stats_per_match()

    
    # Initialize page number in session state if not already set
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

    # Display results for each match with pagination
    page_size = 5  # Number of matches to display per page
    total_matches = len(stats_per_match.index)
    total_pages = (total_matches // page_size) + (1 if total_matches % page_size > 0 else 0)

    start_index = (st.session_state.page_number - 1) * page_size
    end_index = start_index + page_size

    # Display matches for the current page
    for i, vote in enumerate(stats_per_match[start_index:end_index].iterrows()):
        index = start_index + i + 1
        display_total_match_result(metadata_handler, vote[1], index)


    # Pagination controls
    display_pagination(total_pages)


if __name__ == "__main__":
    main() 