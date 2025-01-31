import streamlit as st
import pandas as pd
import os
from utils.contest_sidebar import load_contest_df
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.metadata_handler import MetadataHandler, get_metadata_handler

def display_match_stats(metadata_handler: MetadataHandler, stats_handler: StatsHandler, match_number: int):
    """매치의 통계와 결과를 시각적으로 표시합니다."""
    match_data = metadata_handler.get_match_metadata(match_number)
    
    st.write(f"### 매치 {match_number}")
    
    # 태그 표시
    if match_data and 'tags' in match_data[0]:
        st.write("태그:", ", ".join(eval(match_data[0]['tags'])))
    
    # 통계 데이터 로드
    stats = pd.read_csv(stats_handler.stats_path)
    vote_stats = pd.read_json(stats['vote_percentage'].iloc[0])
    match_stats = vote_stats['match_number'][str(match_number)]
    
    # 가장 많이 선택된 옵션 찾기
    most_voted = max(match_stats.items(), key=lambda x: x[1])[0]
    
    # 이미지/영상 표시
    col1, col2 = st.columns(2)
    for data in match_data:
        filename = data['filename']
        option = data['option']
        model = data.get('model', '')
        votes = match_stats.get(option, 0)
        total_votes = sum(match_stats.values())
        vote_percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        
        # 파일 경로
        file_path = os.path.join(metadata_handler.contest_dir, filename)
        
        # 가장 많은 표를 받은 옵션 표시
        border_color = "green" if option == most_voted else "gray"
        
        with col1 if option == match_data[0]['option'] else col2:
            if filename.lower().endswith(('.mp4', '.mov')):
                st.video(file_path)
            else:
                st.image(file_path)
            st.write(f"모델: {model}")
            st.markdown(
                f"<div style='border:2px solid {border_color};padding:10px'>"
                f"옵션: {option}<br>"
                f"득표: {votes}표 ({vote_percentage:.1f}%)"
                f"</div>",
                unsafe_allow_html=True
            )

def main():
    st.title("투표 결과 상세보기")

    # 세션 초기화
    SessionManager.init_session()

    if 'votes' in st.session_state and len(st.session_state.votes) > 0:
        SessionManager.save_votes_and_reset()
    
    # 컨테스트 목록 로드
    contests_df = load_contest_df()
    
    # 컨테스트 선택
    selected_contest = st.selectbox(
        "컨테스트 선택",
        contests_df['contest_name'].tolist()
    )
    
    contest = contests_df[contests_df['contest_name'] == selected_contest].iloc[0]
    metadata_handler = get_metadata_handler(contest['dir_path'])
    stats_handler = StatsHandler(contest['dir_path'])
    
    # 매치 번호 선택
    metadata_df = metadata_handler.read_metadata()
    match_numbers = sorted(metadata_df['match_number'].unique())
    
    selected_match = st.selectbox(
        "매치 선택",
        match_numbers
    )
    
    # 선택된 매치의 통계 표시
    display_match_stats(metadata_handler, stats_handler, selected_match)
    
    # 뒤로가기 버튼
    if st.button("통계 화면으로 돌아가기"):
        st.switch_page("pages/page3_stats.py")

if __name__ == "__main__":
    main() 