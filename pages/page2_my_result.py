import os
import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.metadata_handler import MetadataHandler
import plotly.express as px

def load_my_votes(contest_dir: str):
    """현재 세션의 투표 결과를 불러옵니다."""
    # load form votes.csv
    votes_file = os.path.join(contest_dir, "votes.csv")
    votes_df = pd.read_csv(votes_file)
    # filter by session_id, make it list
    ret =  votes_df[votes_df['session_id'] == st.session_state['session_id']].to_dict(orient='records')

    # TODO: filter by user_id

    return ret
    

def display_vote_summary(contest_id: str):
    """특정 컨테스트에 대한 투표 요약을 표시합니다."""

    contest_dir = os.path.join("data", "contests", contest_id)
    votes = load_my_votes(contest_dir)

    contest_votes = [v for v in votes]
    if not contest_votes:
        st.write("아직 투표 결과가 없습니다.")
        if st.button("투표하러 가기"):
            # TODO: add contest_id to query params
            st.switch_page("pages/page1_vote.py")
        return
    

    # 투표 통계 계산
    vote_counts = {}
    for vote in contest_votes:
        option = vote['chosen_option']
        vote_counts[option] = vote_counts.get(option, 0) + 1
    
    # 결과 표시
    st.write("### 내 투표 결과")
    st.write(f"전체 투표 횟수: {len(contest_votes)}회")

    # 모델별 투표 수 계산
    model_votes = {}
    for vote in contest_votes:
        model = vote['model']
        model_votes[model] = model_votes.get(model, 0) + 1
    
    # Plotly를 사용하여 파이 차트 생성
    fig = px.pie(
        values=list(model_votes.values()),
        names=list(model_votes.keys()),
        title='모델별 투표 비율',
        hole=0.3  # 도넛 차트 스타일을 위한 설정 (선택사항)
    )
    
    # 차트 레이아웃 설정
    fig.update_layout(
        title_x=0.5,  # 제목 중앙 정렬
        title_font_size=20
    )
    
    # Streamlit에 차트 표시
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("내 투표 결과")
    
    # 세션 초기화
    SessionManager.init_session()

    # TODO: check session, if votes remain, save votes and reset session

    
    # 컨테스트 목록 로드
    contests_df = pd.read_csv("data/contests.csv")
    
    # 각 컨테스트별 결과 표시
    for _, contest in contests_df.iterrows():
        st.write(f"## {contest['contest_name']}")
        display_vote_summary(str(contest['contest_id']))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("남들 결과 보기", key=f"others_{contest['contest_id']}"):
                st.switch_page("pages/page3_stats.py")
        with col2:
            if st.button("내 선택 돌아보기", key=f"review_{contest['contest_id']}"):
                st.switch_page("pages/page4_my_choice.py")

if __name__ == "__main__":
    main() 