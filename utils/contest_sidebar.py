import pandas as pd
import streamlit as st

@st.cache_data
def load_contest_df():
    return pd.read_csv("data/contests.csv")

def load_contests():
    """contests.csv에서 컨테스트 목록을 로드합니다."""
    contests_df = load_contest_df()
    return contests_df.sort_values('contest_start_date', ascending=False)

def display_contest_sidebar(contest_id=None):
    """사이드바에 컨테스트 목록을 표시합니다."""
    contests = load_contests()

    contest_index = 0
    if not contest_id:
        #TODO get default contest from somewhere else. (popular? or promoted?)
        contest_index = 0 
    elif contest_id in contests['contest_id'].values:
        contest_index = int(contests.index[contests['contest_id'] == contest_id][0])

    selected_contest = st.sidebar.selectbox(
        "컨테스트 선택",
        contests['contest_name'].tolist(),
        index=contest_index
    )
    st.session_state['last_contest_id'] = int(contests.loc[contests['contest_name'] == selected_contest, 'contest_id'])
    st.sidebar.markdown("---")
    display_page_sidebar_with_page()

    ret_df = contests[contests['contest_name'] == selected_contest]
    return ret_df.iloc[0] 


def display_page_sidebar_with_page():

    st.sidebar.page_link("./pages/vote.py", label="투표하기", icon="✅")
    st.sidebar.page_link("./pages/results.py", label="내 결과 보기", icon="👀")
    st.sidebar.page_link("./pages/choices.py", label="내 선택 보기", icon="🔍")
    st.sidebar.page_link("./pages/stats.py", label="전체 통계 보기", icon="📊")
    st.sidebar.page_link("./pages/statsdetail.py", label="전체 선택 보기", icon="🌄")
    st.sidebar.page_link("./pages/shared.py", label="공유된 결과 보기", icon="📋", disabled=True)

