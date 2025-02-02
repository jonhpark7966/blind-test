import os
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.session_manager import SessionManager
from utils.contest_sidebar import display_contest_sidebar
from utils.stats_handler import StatsHandler
from utils.vote_display import display_charts


def display_all_vote_summary(contest_id: str):
    contest_dir = os.path.join("data", "contests", contest_id)

    stats_handler = StatsHandler(contest_dir)

    model_counts = stats_handler.load_stats()
    tag_counts_per_model = stats_handler.load_stats_per_tag()

    st.write(f"전체 투표 횟수: {model_counts.sum()}회")
    
    display_charts(model_counts, tag_counts_per_model, "") 




def main():
    st.title("전체 투표 결과")
    
    # 세션 초기화
    SessionManager.init_session()

    if 'votes' in st.session_state and len(st.session_state.votes) > 0:
        SessionManager.save_votes_and_reset()
    
    # 사이드바에 컨테스트 목록 표시
    default_contest_id = st.session_state.get('last_contest_id')
    contest = display_contest_sidebar(default_contest_id)

    # 선택된 컨테스트의 결과 표시
    display_all_vote_summary(str(contest['contest_id']))

    col1, _ = st.columns(2)  # Unpack the columns correctly
    with col1:
        if st.button("다수의 선택 확인하기"):
            st.switch_page("pages/page5_others_choice.py")

if __name__ == "__main__":
    main() 