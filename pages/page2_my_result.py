import ast
from functools import reduce
import os
import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
import plotly.express as px
from utils.contest_sidebar import display_contest_sidebar
from utils.share_link_generator import generate_shareable_link
from utils.votes_handler import load_my_votes
import plotly.graph_objects as go
from utils.vote_display import display_vote_results

def display_vote_summary(contest_id: str):
    contest_dir = os.path.join("data", "contests", contest_id)
    votes = load_my_votes(contest_dir)

    contest_votes = [v for v in votes]
    if not contest_votes:
        st.write("아직 투표 결과가 없습니다.")
        if st.button("투표하러 가기"):
            st.switch_page("pages/page1_vote.py")
        return
    
    st.write("### 내 투표 결과")
    st.write(f"전체 투표 횟수: {len(contest_votes)}회")
    
    display_vote_results(contest_votes)

    # Generate shareable link
    try:
        share_link = generate_shareable_link(contest_id)
        st.write(f"Share this link to view your results: {share_link}")
    except ValueError as e:
        st.error(f"Error generating shareable link: {e}")

def main():
    st.title("내 투표 결과")
    SessionManager.init_session()

    if 'votes' in st.session_state and len(st.session_state.votes) > 0:
        SessionManager.save_votes_and_reset()
    
    default_contest_id = st.session_state.get('last_contest_id')
    contest = display_contest_sidebar(default_contest_id)
    
    display_vote_summary(str(contest['contest_id']))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("남들 결과 보기"):
            st.switch_page("pages/page3_stats.py")
    with col2:
        if st.button("내 선택 돌아보기"):
            st.switch_page("pages/page4_my_choice.py")

if __name__ == "__main__":
    main()