from datetime import datetime
import uuid
import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import pillow_heif
from utils.metadata_handler import MetadataHandler, get_metadata_handler
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.contest_sidebar import display_contest_sidebar, load_contest_df  # Import the function
from utils.media_handler import load_media, display_media
from utils.tag_styler import display_tags

def get_random_match(metadata_handler):
    """랜덤한 매치를 선택합니다. 이미 투표한 매치는 제외합니다."""
    matches = metadata_handler.get_matches()
    if not matches:
        return None

    # 이미 투표한 매치 번호들을 가져옴
    voted_matches = set()
    if 'votes' in st.session_state:
        voted_matches = {vote['match_number'] for vote in st.session_state.votes}
    
    # 아직 투표하지 않은 매치들만 필터링
    available_matches = [match for match in matches if match.get('Match') and match['Match'] not in voted_matches]
    
    if not available_matches:
        return None  # 모든 매치에 대해 투표 완료
    
    # 매치 번호로 그룹화
    match_groups = {}
    for match in available_matches:
        match_num = match['Match']
        if match_num:
            if match_num not in match_groups:
                match_groups[match_num] = []
            match_groups[match_num].append(match['FileName'])
    
    # 랜덤한 매치 선택
    if not match_groups:
        return None
        
    match_number = random.choice(list(match_groups.keys()))
    pair = match_groups[match_number]
    random.shuffle(pair)
    random.shuffle(matches)
    return pair[0], pair[1], match_number


def main():
    # 세션 초기화
    SessionManager.init_session()

    # 컨테스트 선택
    contest = display_contest_sidebar()

    # Get MetadataHandler for the selected contest
    metadata_handler = get_metadata_handler(contest['dir_path'])
    
    # 타이틀 표시
    st.title(contest['contest_name'])
    st.write(contest['contest_description'])
    
    # 현재 매치 가져오기 또는 새로운 매치 선택
    if 'current_contest_id' not in st.session_state or st.session_state.current_contest_id != contest['contest_id']:
        st.session_state.current_contest_id = contest['contest_id']
        match_data = get_random_match(metadata_handler)
        if match_data:
            st.session_state.current_pair = match_data
    
    if 'current_pair' in st.session_state:
        file1, file2, match_number = st.session_state.current_pair
        
        # 미디어 로드
        media1 = load_media(os.path.join(contest['dir_path'], file1), metadata_handler)
        media2 = load_media(os.path.join(contest['dir_path'], file2), metadata_handler)

        # get all length of matches
        all_matches = metadata_handler.get_matches()
        # count unique match numbers (key is 'Match')
        all_matches_length = len(set(item['Match'] for item in all_matches))

        # get length of matches that user has voted
        voted_matches = set()
        if 'votes' in st.session_state:
            voted_matches = {vote['match_number'] for vote in st.session_state.votes}
        voted_matches_length = len(voted_matches)

        # display number of matches that user has voted per all contests
        progress_percentage = (voted_matches_length / all_matches_length) * 100
        st.markdown("<br>", unsafe_allow_html=True)  # Add space above
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; text-align: center; font-size: 12px; margin: 0 50px;">
                <strong>Progress:</strong> {voted_matches_length} / {all_matches_length}
                <div style="background-color: transparent; border-radius: 5px; overflow: hidden; margin-top: 5px; margin: 0 10px;">
                    <div style="width: {progress_percentage}%; background-color: white; height: 5px; padding: 2px 0; color: grey; font-size: 10px;">
                        {progress_percentage:.1f}%
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)  # Add space below

        file1_name = os.path.basename(file1)
        tags = metadata_handler.get_tags(file1_name)

        # Container for tags (on the left) and submit button (on the right)
        row_tags, row_submit  = st.columns([0.6, 0.4], gap='large', vertical_alignment='center')

        with row_tags:
            display_tags(tags)

        with row_submit:
            if st.button('투표 끝내고, 결과보기', key='submit-button', type='primary', use_container_width=True):
                if 'votes' in st.session_state and len(st.session_state.votes) > 0:
                    st.success("투표가 완료되었습니다! 결과 페이지로 이동합니다.")
                    SessionManager.save_votes_and_reset()
                    st.session_state['last_contest_id'] = contest['contest_id']
                    st.switch_page("pages/page2_my_result.py")


        st.markdown("---")
        # 화면 분할 및 미디어 표시
        col1, col2 = st.columns(2)

        with col1:
            if st.button('↓ 선택', key=f'button1_{match_number}'):
                if 'votes' not in st.session_state:
                    st.session_state.votes = []
                st.session_state.votes.append({
                    'match_number': match_number,
                    'selected': file1,
                    'not_selected': file2,
                    'contest_id': contest['contest_id'],
                    'contest_dir': contest['dir_path']
                })
                match_data = get_random_match(metadata_handler)
                if match_data:
                    st.session_state.current_pair = match_data
                    st.rerun()
                else:
                    st.success("모든 투표가 완료되었습니다!")
            display_media(col1, media1)
            
        
        with col2:     
            if st.button('↓ 선택', key=f'button2_{match_number}'):
                if 'votes' not in st.session_state:
                    st.session_state.votes = []
                st.session_state.votes.append({
                    'match_number': match_number,
                    'selected': file2,
                    'not_selected': file1,
                    'contest_id': contest['contest_id'],
                    'contest_dir': contest['dir_path']
                })
                match_data = get_random_match(metadata_handler)
                if match_data:
                    st.session_state.current_pair = match_data
                    st.rerun()
                else:
                    st.success("모든 투표가 완료되었습니다!")
                
            display_media(col2, media2)
        


if __name__ == "__main__":
    main() 