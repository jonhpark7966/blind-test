import pandas as pd
import streamlit as st

@st.cache_data
def load_contest_df():
    return pd.read_csv("data/contests.csv")

def load_contests():
    """contests.csv에서 컨테스트 목록을 로드합니다."""
    contests_df = load_contest_df()
    return contests_df.sort_values('contest_start_date', ascending=False)

def display_contest_sidebar(default_contest_id=None):
    """사이드바에 컨테스트 목록을 표시합니다."""
    contests = load_contests()
    selected_contest = st.sidebar.selectbox(
        "컨테스트 선택",
        contests['contest_name'].tolist(),
        index=0  # 첫 번째 컨테스트를 기본 선택
    )

    ret_df = contests[contests['contest_name'] == selected_contest]
    return ret_df.iloc[0] 


def display_page_sidebar_with_page():

    pages = {
    "Your account": [
        st.Page("./app_pages/page1_vote.py", title="Create your account"),
        st.Page("./app_pages/page2_my_result.py", title="Manage your account"),
    ],
    "Resources": [
        st.Page("./app_pages/page3_stats.py", title="Learn about us"),
        st.Page("./app_pages/page4_my_choice.py", title="Try it out"),
    ],
    }

    pg = st.navigation(pages)
    pg.run()