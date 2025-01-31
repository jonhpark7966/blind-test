import os
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.session_manager import SessionManager
from utils.contest_sidebar import display_contest_sidebar

def load_votes(contest_dir: str):
    """Load votes from the specified contest directory."""
    votes_file = os.path.join(contest_dir, "votes.csv")
    if not os.path.exists(votes_file):
        return pd.DataFrame()
    return pd.read_csv(votes_file)

def display_aggregated_results(votes_df: pd.DataFrame):
    """Display aggregated voting results."""
    if votes_df.empty:
        st.write("아직 투표 결과가 없습니다.")
        return
    
    # Aggregate vote counts by model and tag
    vote_summary = votes_df.groupby(['model', 'tag']).size().reset_index(name='count')
    
    # Display results using a sunburst chart
    fig = px.sunburst(
        vote_summary,
        path=['model', 'tag'],
        values='count',
        title='모델 및 태그별 투표 분포',
    )
    st.plotly_chart(fig, use_container_width=True)

def load_all_votes(contest_dir: str):
    """Load all votes from the specified contest directory."""
    votes_file = os.path.join(contest_dir, "votes.csv")
    if not os.path.exists(votes_file):
        return pd.DataFrame()
    return pd.read_csv(votes_file)

def display_all_vote_summary(contest_id: str):
    """Display a summary of all votes for a specific contest."""
    contest_dir = os.path.join("data", "contests", contest_id)
    votes_df = load_all_votes(contest_dir)

    if votes_df.empty:
        st.write("아직 투표 결과가 없습니다.")
        return

    # Display total number of votes
    total_votes = len(votes_df)
    st.write(f"전체 투표 횟수: {total_votes}회")

    # 모델과 태그 조합별 투표 수 계산
    vote_data = []
    for _, vote in votes_df.iterrows():  # Iterate over the DataFrame rows
        vote_data.append({
            'model': vote['model'],
            'tag': vote['tag'],
            'count': 1
        })
    
    # DataFrame 생성 및 그룹화
    vote_df = pd.DataFrame(vote_data)
    
    # Convert 'model' and 'tag' columns to string to avoid type errors
    vote_df['model'] = vote_df['model'].astype(str)
    vote_df['tag'] = vote_df['tag'].astype(str)
    
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

    # Create a stacked pie chart
    fig = px.sunburst(
        filtered_df,
        path=['model', 'tag'],
        values='count',
        title='모델 및 태그별 전체 투표 분포',
       
    )
    
    # Add percentage and count to the chart
    fig.update_layout(
        title_x=0.5,  # 제목 중앙 정렬
        title_font_size=20,
    )
    fig.update_traces(
        textinfo='label+value+percent entry',
        insidetextfont=dict(size=12),
        textfont=dict(size=12, color='black'),  # Set text color and size
        insidetextorientation='horizontal'  # Keep text horizontal
    )

    # Streamlit에 차트 표시
    st.plotly_chart(fig, use_container_width=True)

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
            st.switch_page("pages/page5_other_choice.py")

if __name__ == "__main__":
    main() 