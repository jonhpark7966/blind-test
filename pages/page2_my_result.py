import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.metadata_handler import MetadataHandler

def load_my_votes():
    """현재 세션의 투표 결과를 불러옵니다."""
    return SessionManager.get_votes()

def display_vote_summary(contest_id: str, votes: list):
    """특정 컨테스트에 대한 투표 요약을 표시합니다."""
    contest_votes = [v for v in votes if v['contest_id'] == contest_id]
    if not contest_votes:
        st.write("아직 투표 결과가 없습니다.")
        if st.button("투표하러 가기"):
            st.switch_page("pages/page1_vote.py")
        return
    
    # 투표 통계 계산
    vote_counts = {}
    for vote in contest_votes:
        option = vote['chosen_option']
        vote_counts[option] = vote_counts.get(option, 0) + 1
    
    # 결과 표시
    st.write("### 내 투표 결과")
    for option, count in vote_counts.items():
        percentage = (count / len(contest_votes)) * 100
        st.write(f"{option}: {count}회 ({percentage:.1f}%)")

def main():
    st.title("내 투표 결과")
    
    # 세션 초기화
    SessionManager.init_session()
    
    # 투표 데이터 로드
    my_votes = load_my_votes()
    if not my_votes:
        st.write("아직 투표 이력이 없습니다.")
        if st.button("투표하러 가기"):
            st.switch_page("pages/page1_vote.py")
        return
    
    # 컨테스트 목록 로드
    contests_df = pd.read_csv("data/contests.csv")
    
    # 각 컨테스트별 결과 표시
    for _, contest in contests_df.iterrows():
        st.write(f"## {contest['contest_name']}")
        display_vote_summary(contest['contest_id'], my_votes)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("남들 결과 보기", key=f"others_{contest['contest_id']}"):
                st.switch_page("pages/page3_stats.py")
        with col2:
            if st.button("내 선택 돌아보기", key=f"review_{contest['contest_id']}"):
                st.switch_page("pages/page4_my_choice.py")

if __name__ == "__main__":
    main() 