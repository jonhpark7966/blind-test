import streamlit as st
import pandas as pd
import random
import os

# 앱 제목
st.title("Video Blind Test")

# 세션 상태 초기화
if 'votes' not in st.session_state:
    st.session_state.votes = []

@st.cache_data
def load_metadata():
    return pd.read_csv('./2/video_metadata.csv')

metadata = load_metadata()

# 임의 매치 선택 함수
def get_random_match():
    matches = metadata['Match'].unique()
    match = random.choice(matches)
    pair = metadata[metadata['Match'] == match]
    videos = pair['File:FileName'].tolist()
    random.shuffle(videos)
    return videos[0], videos[1]

# 비디오 파일 로드 함수
def load_video_bytes(path):
    full_path = os.path.join('./2', path)
    with open(full_path, 'rb') as f:
        return f.read()

# 현재 매치가 세션에 없으면 새로 랜덤 매치 할당
if 'current_pair' not in st.session_state:
    st.session_state.current_pair = get_random_match()

# 비디오 2개 불러오기
video1 = load_video_bytes(st.session_state.current_pair[0])
video2 = load_video_bytes(st.session_state.current_pair[1])

col1, col2 = st.columns(2)

# 왼쪽 비디오
with col1:
    st.video(video1)
    if st.button('Select Left'):
        st.session_state.votes.append({
            'selected': st.session_state.current_pair[0],
            'not_selected': st.session_state.current_pair[1]
        })
        st.session_state.current_pair = get_random_match()
        st.rerun()

# 오른쪽 비디오
with col2:
    st.video(video2)
    if st.button('Select Right'):
        st.session_state.votes.append({
            'selected': st.session_state.current_pair[1],
            'not_selected': st.session_state.current_pair[0]
        })
        st.session_state.current_pair = get_random_match()
        st.rerun()

# 투표 종료 버튼
if st.button('End Voting'):
    if len(st.session_state.votes) > 0:
        results_df = pd.DataFrame(st.session_state.votes)
        selected_models = results_df['selected'].map(metadata.set_index('File:FileName')['Model'])
        total_votes = len(st.session_state.votes)
        s24_ultra_votes = sum(selected_models == 'SM-S928N')
        iphone_16_pro_max_votes = sum(selected_models == 'iPhone 16 Pro Max')

        st.write(f"총 투표 횟수: {total_votes}")
        st.write(f"Galaxy S24 Ultra 선택 횟수: {s24_ultra_votes}")
        st.write(f"iPhone 16 Pro Max 선택 횟수: {iphone_16_pro_max_votes}")

        # 다음 투표 준비 위해 세션 초기화
        st.session_state.votes = []
        st.session_state.current_pair = get_random_match()