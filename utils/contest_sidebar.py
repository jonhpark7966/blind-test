import pandas as pd
import streamlit as st

def load_contests():
    """contests.csv에서 컨테스트 목록을 로드합니다."""
    contests_df = pd.read_csv("data/contests.csv")
    return contests_df.sort_values('contest_start_date', ascending=False)

def display_contest_sidebar():
    """사이드바에 컨테스트 목록을 표시합니다."""
    contests = load_contests()
    selected_contest = st.sidebar.selectbox(
        "컨테스트 선택",
        contests['contest_name'].tolist(),
        index=0  # 첫 번째 컨테스트를 기본 선택
    )
    ret_df = contests[contests['contest_name'] == selected_contest]
    return ret_df.iloc[0] 