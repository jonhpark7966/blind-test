import os
import streamlit as st
import pandas as pd
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.metadata_handler import MetadataHandler
import plotly.express as px
from utils.contest_sidebar import display_contest_sidebar  # Import the function

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
    

    # 투표 통계 계산 및 결과 표시 부분
    st.write("### 내 투표 결과")
    st.write(f"전체 투표 횟수: {len(contest_votes)}회")

    # 모델과 태그 조합별 투표 수 계산
    vote_data = []
    for vote in contest_votes:
        vote_data.append({
            'model': vote['model'],
            'tag': vote['tag'],
            'count': 1
        })
    
    # DataFrame 생성 및 그룹화
    vote_df = pd.DataFrame(vote_data)
    
    # 필터 추가
    col1, col2 = st.columns(2)
    with col1:
        selected_models = st.multiselect(
            "모델 선택",
            options=sorted(vote_df['model'].unique()),
            default=sorted(vote_df['model'].unique())
        )
    with col2:
        selected_tags = st.multiselect(
            "태그 선택",
            options=sorted(vote_df['tag'].unique()),
            default=sorted(vote_df['tag'].unique())
        )
    
    # 필터 적용
    filtered_df = vote_df[
        (vote_df['model'].isin(selected_models)) &
        (vote_df['tag'].isin(selected_tags))
    ]
    
    # 그룹화 적용
    filtered_df = filtered_df.groupby(['model', 'tag'])['count'].sum().reset_index()

    if len(filtered_df) > 0:
        # Sunburst 차트 생성
        fig = px.sunburst(
            filtered_df,
            path=['model', 'tag'],
            values='count',
            title='모델 및 태그별 투표 분포',
        )
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title_x=0.5,  # 제목 중앙 정렬
            title_font_size=20,
        )
        
        # 텍스트 표시 설정
        fig.update_traces(
            textinfo='label+text+value+percent parent',
            insidetextfont=dict(size=12)
        )
        
        # Streamlit에 차트 표시
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("선택한 필터에 해당하는 데이터가 없습니다.")

def main():
    st.title("내 투표 결과")
    
    # 세션 초기화
    SessionManager.init_session()

    if 'votes' in st.session_state and len(st.session_state.votes) > 0:
        SessionManager.save_votes_and_reset()
    
    # 사이드바에 컨테스트 목록 표시
    contest = display_contest_sidebar()
    
    # 선택된 컨테스트의 결과 표시
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