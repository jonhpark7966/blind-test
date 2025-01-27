import streamlit as st
import pandas as pd
import os
from utils.session_manager import SessionManager
from utils.metadata_handler import MetadataHandler

def display_match_result(metadata_handler: MetadataHandler, match_number: int, chosen_option: str):
    """매치의 결과를 시각적으로 표시합니다."""
    match_data = metadata_handler.get_match_metadata(match_number)
    
    st.write(f"### 매치 {match_number}")
    
    # 태그 표시
    if match_data and 'tags' in match_data[0]:
        st.write("태그:", ", ".join(eval(match_data[0]['tags'])))
    
    # 이미지/영상 표시
    col1, col2 = st.columns(2)
    for data in match_data:
        filename = data['filename']
        option = data['option']
        model = data.get('model', '')
        
        # 파일 경로
        file_path = os.path.join(metadata_handler.contest_dir, filename)
        
        # 선택여부에 따른 테두리 스타일
        border_color = "green" if option == chosen_option else "gray"
        
        with col1 if option == match_data[0]['option'] else col2:
            if filename.lower().endswith(('.mp4', '.mov')):
                st.video(file_path)
            else:
                st.image(file_path)
            st.write(f"모델: {model}")
            st.markdown(f"<div style='border:2px solid {border_color};padding:10px'>선택: {option}</div>", 
                       unsafe_allow_html=True)

def main():
    st.title("내가 선택한 후보 상세보기")
    
    # 세션 초기화
    SessionManager.init_session()
    
    # 컨테스트 목록 로드
    contests_df = pd.read_csv("data/contests.csv")
    
    # 컨테스트 선택
    selected_contest = st.selectbox(
        "컨테스트 선택",
        contests_df['contest_name'].tolist()
    )
    
    contest = contests_df[contests_df['contest_name'] == selected_contest].iloc[0]
    metadata_handler = MetadataHandler(contest['dir_path'])
    
    # 내 투표 결과 로드
    my_votes = [v for v in SessionManager.get_votes() 
                if v['contest_id'] == contest['contest_id']]
    
    if not my_votes:
        st.write("이 컨테스트에 대한 투표 결과가 없습니다.")
        if st.button("투표하러 가기"):
            st.switch_page("pages/page1_vote.py")
        return
    
    # 각 매치별 결과 표시
    for vote in my_votes:
        display_match_result(metadata_handler, vote['match_number'], vote['chosen_option'])

if __name__ == "__main__":
    main() 