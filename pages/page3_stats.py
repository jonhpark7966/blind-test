import streamlit as st
import pandas as pd
import plotly.express as px
from utils.stats_handler import StatsHandler
from utils.metadata_handler import MetadataHandler

def load_contest_stats(contest_dir: str):
    """컨테스트의 통계 데이터를 로드합니다."""
    stats_handler = StatsHandler(contest_dir)
    stats = pd.read_csv(os.path.join(contest_dir, "stats.csv"))
    return stats

def display_contest_stats(contest: pd.Series):
    """컨테스트의 통계를 시각화하여 표시합니다."""
    stats = load_contest_stats(contest['dir_path'])
    if stats.empty:
        st.write("아직 투표 결과가 없습니다.")
        return
    
    # 전체 통계 표시
    st.write(f"### 전체 투표 결과")
    vote_data = pd.read_json(stats['vote_percentage'].iloc[0])['total']
    
    # 파이 차트로 표시
    fig = px.pie(
        values=list(vote_data.values()),
        names=list(vote_data.keys()),
        title="전체 투표 비율"
    )
    st.plotly_chart(fig)
    
    # 매치별 통계
    st.write("### 매치별 투표 결과")
    match_data = pd.read_json(stats['vote_percentage'].iloc[0])['match_number']
    for match_num, match_stats in match_data.items():
        if st.button(f"매치 {match_num} 상세보기"):
            st.switch_page("pages/page5_others_choice.py")

def main():
    st.title("전체 투표 통계")
    
    # 컨테스트 목록 로드
    contests_df = pd.read_csv("data/contests.csv")
    
    # 컨테스트 선택
    selected_contest = st.selectbox(
        "컨테스트 선택",
        contests_df['contest_name'].tolist()
    )
    
    # 선택된 컨테스트의 통계 표시
    contest = contests_df[contests_df['contest_name'] == selected_contest].iloc[0]
    display_contest_stats(contest)

if __name__ == "__main__":
    main() 