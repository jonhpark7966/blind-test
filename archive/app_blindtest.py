import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import pillow_heif  # 상단에 추가

# 앱 제목 설정
st.title("Image Blind Test")

# 세션 상태 초기화
if 'votes' not in st.session_state:
    st.session_state.votes = []

# metadata.csv 읽기
@st.cache_data
def load_metadata():
    return pd.read_csv('./1/metadata.csv')

metadata = load_metadata()

# 이미지 로드 함수 수정
def load_image(image_path):
    full_path = os.path.join('./1', image_path)
    if image_path.lower().endswith('.heic'):
        heif_file = pillow_heif.read_heif(full_path)
        img = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
    else:
        # Rotate based on metadata "Orientation"ß
        img = Image.open(full_path)
        if metadata[metadata['FileName'] == image_path]["Orientation"].values[0] == "Rotate 90 CW":
            img = img.rotate(-90, expand=True)
        elif metadata[metadata['FileName'] == image_path]["Orientation"].values[0] == "Rotate 90 CCW":
            img = img.rotate(90, expand=True)
        elif metadata[metadata['FileName'] == image_path]["Orientation"].values[0] == "Rotate 180":
            img = img.rotate(180, expand=True)
    
    return img

# 랜덤 매치 선택
def get_random_match():
    # 모든 매치 번호 가져오기
    matches = metadata['Match'].unique()
    
    # 랜덤하게 매치 선택
    match = random.choice(matches)
    
    # 해당 Match의 이미지 쌍 가져오기
    pair = metadata[metadata['Match'] == match]
    images = pair['FileName'].tolist()
    # 이미지 순서 랜덤화
    random.shuffle(images)
    return images[0], images[1]

# 메인 인터페이스
col1, col2 = st.columns(2)

if 'current_pair' not in st.session_state:
    st.session_state.current_pair = get_random_match()

# 두 이미지 로드
img1 = load_image(st.session_state.current_pair[0])
img2 = load_image(st.session_state.current_pair[1])

# 이미지 표시
with col1:
    st.image(img1, use_container_width=True)
    if st.button('Select Left'):
        st.session_state.votes.append({
            'selected': st.session_state.current_pair[0],
            'not_selected': st.session_state.current_pair[1]
        })
        st.session_state.current_pair = get_random_match()
        st.rerun()

with col2:
    st.image(img2, use_container_width=True)
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
        # 결과를 DataFrame으로 변환
        results_df = pd.DataFrame(st.session_state.votes)
        
        # 선택된 파일명들을 metadata와 매칭하여 모델 정보 가져오기
        selected_models = results_df['selected'].map(metadata.set_index('FileName')['Model'])
        
        # 통계 계산
        total_votes = len(st.session_state.votes)
        s24_ultra_votes = sum(selected_models == 'Galaxy S24 Ultra')
        iphone_16_pro_max_votes = sum(selected_models == 'iPhone 16 Pro Max')
        
        # 결과 표시
        st.write(f"총 투표 횟수: {total_votes}")
        st.write(f"Galaxy S24 Ultra 선택 횟수: {s24_ultra_votes}")
        st.write(f"iPhone 16 Pro Max 선택 횟수: {iphone_16_pro_max_votes}")
        
        # 세션 상태 초기화
        st.session_state.votes = []
        st.session_state.current_pair = get_random_match()
 