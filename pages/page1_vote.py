import streamlit as st
import pandas as pd
import os
from utils.metadata_handler import MetadataHandler
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler

def load_contests():
    """contests.csv에서 컨테스트 목록을 로드합니다."""
    contests_df = pd.read_csv("data/contests.csv")
    return contests_df.sort_values('contest_start_date', ascending=False)

def display_contest_sidebar():
    """사이드바에 컨테스트 목록을 표시합니다."""
    contests = load_contests()
    selected_contest = st.sidebar.selectbox(
        "컨테스트 선택",
        contests['contest_name'].tolist()
    )
    return contests[contests['contest_name'] == selected_contest].iloc[0]

def main():
    st.title("블라인드 테스트 투표")
    
    # 세션 초기화
    SessionManager.init_session()
    
    # 컨테스트 선택
    contest = display_contest_sidebar()
    
    # 메타데이터 핸들러 초기화
    metadata_handler = MetadataHandler(contest['dir_path'])
    
    # 투표 UI 표시
    st.write(f"## {contest['contest_name']}")
    st.write(contest['contest_description'])
    
    # 여기에 투표 로직 구현
    # ...

if __name__ == "__main__":
    main() 