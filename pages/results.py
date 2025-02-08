import ast
from functools import reduce
import os
import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
import plotly.express as px
from utils.contest_sidebar import display_contest_sidebar
from utils.share_link_generator import generate_shareable_link
from utils.votes_handler import load_my_votes, load_shared_votes
import plotly.graph_objects as go
from utils.vote_display import display_vote_results

from st_copy_to_clipboard import st_copy_to_clipboard


def display_vote_summary(contest_id: str, is_shared: bool, session_id: str):
    contest_dir = os.path.join("data", "contests", contest_id)
    if is_shared:
        votes = load_shared_votes(contest_id, session_id)
    else:
        votes = load_my_votes(contest_dir)

    contest_votes = [v for v in votes]
    if not contest_votes:
        st.write("아직 투표 결과가 없습니다.")
        if st.button("투표하러 가기"):
            st.switch_page("pages/vote.py")
        return

    if not is_shared:
        share_link = generate_shareable_link(contest_id)
        # Render copy to clipboard button
        st_copy_to_clipboard(share_link, "📋 공유 링크 복사하기", "✅ 공유 링크 복사가 완료되었습니다!")

    if is_shared:
        if st.button("나도 투표하러 가기"):
            st.switch_page("pages/vote.py")

    #st.write(f"전체 투표 횟수: {len(contest_votes)}회")
    display_vote_results(contest_votes)

def main():
    SessionManager.init_session()

    if 'votes' in st.session_state and len(st.session_state.votes) > 0:
        SessionManager.save_votes_and_reset()

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

    if is_shared:
        st.title("공유된 투표 결과")
    else:
        st.title("내 투표 결과")

    contest = display_contest_sidebar(contest_id)
    st.query_params['contest_id'] = str(contest['contest_id'])
   
    display_vote_summary(str(contest['contest_id']), is_shared, session_id)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("남들 결과 보기"):
            st.switch_page("pages/stats.py")
    with col2:
        if st.button("선택 돌아보기"):
            # make link and goes to result.
            choice_url = generate_shareable_link(contest_id, session_id, choice_link=True)
            st.markdown(f'<meta http-equiv="refresh" content="0;url={choice_url}">', unsafe_allow_html=True)

if __name__ == "__main__":
    main()