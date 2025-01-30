from datetime import datetime
import uuid
import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import pillow_heif
from utils.metadata_handler import MetadataHandler
from utils.session_manager import SessionManager
from utils.stats_handler import StatsHandler
from utils.contest_sidebar import display_contest_sidebar  # Import the function

def load_media(file_path, metadata_handler):
    """이미지나 비디오 파일을 로드합니다."""
    file_ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.heic']:
        if file_ext == '.heic':
            heif_file = pillow_heif.read_heif(file_path)
            img = Image.frombytes(
                heif_file.mode, 
                heif_file.size, 
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
        else:
            # GALAXY Orient handling
            img = Image.open(file_path)
        
            # metadata_handler에서 orientation 정보 가져오기
            orientation = metadata_handler.get_orientation(file_name)

            # orientation에 따라 이미지 회전
            if orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 5:
                img = img.rotate(90, expand=True)
            elif orientation == 8:
                img = img.rotate(180, expand=True)
        
        return img
    else:  # 비디오 파일
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
    
        if file_ext in ['.mov', '.mp4', '.avi']:
            return file_path
        else:
            return None
       # with open(file_path, 'rb') as f:
           # return f.read()



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

def display_media(col, media, file_path, is_video=False):
    """미디어를 화면에 표시합니다."""
    if is_video:
        col.video(media)
    else:
        col.image(media, use_container_width=True)

def main():
    # 세션 초기화
    SessionManager.init_session()
    
    # 컨테스트 선택
    contest = display_contest_sidebar()
    
    # metadata_handlers 딕셔너리를 세션에서 초기화
    if 'metadata_handlers' not in st.session_state:
        st.session_state.metadata_handlers = {}
    
    # 현재 컨테스트의 metadata_handler가 없으면 생성
    if contest['contest_id'] not in st.session_state.metadata_handlers:
        st.session_state.metadata_handlers[contest['contest_id']] = MetadataHandler(contest['dir_path'], read_from_csv=True)
    
    metadata_handler = st.session_state.metadata_handlers[contest['contest_id']]
    
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
        
        # 미디어 타입 확인
        is_video = any(file1.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi'])
        
        # 미디어 로드
        media1 = load_media(os.path.join(contest['dir_path'], file1), metadata_handler)
        media2 = load_media(os.path.join(contest['dir_path'], file2), metadata_handler)
        
        # 화면 분할 및 미디어 표시
        col1, col2 = st.columns(2)
        
        with col1:
            file1_name = os.path.basename(file1)
            tag = metadata_handler.get_tag(file1_name)
            if tag:  # If tag exists
                st.write(f"{tag}")  # Display tag directly as a string
            
            display_media(col1, media1, file1, is_video)
            if st.button('왼쪽 선택'):
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
                    # 모든 매치 완료 시 결과 페이지로 이동
                    st.success("모든 투표가 완료되었습니다!")
                    SessionManager.save_votes_and_reset()
        
        with col2:
            file2_name = os.path.basename(file2)
            tag = metadata_handler.get_tag(file2_name)
            if tag:  # If tag exists
                st.write(f"{tag}")  # Display tag directly as a string
            display_media(col2, media2, file2, is_video)
            if st.button('오른쪽 선택'):
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
                    # 모든 매치 완료 시 결과 페이지로 이동
                    SessionManager.save_votes_and_reset()
                    st.success("모든 투표가 완료되었습니다!")
        
        # Submit 버튼 (투표 종료)
        if st.button('Submit'):
            if 'votes' in st.session_state and len(st.session_state.votes) > 0:
                st.success(f"투표가 완료되었습니다! 결과 페이지로 이동합니다.")
                SessionManager.save_votes_and_reset()
                st.switch_page("pages/page2_my_result.py")
                st.stop()

if __name__ == "__main__":
    main() 