import streamlit as st
from PIL import Image
import os
import random
import csv
import uuid
from datetime import datetime  # Python의 datetime 모듈 사용

# 이미지 디렉토리 설정
IMAGE_DIR = "images"

# CSV 저장 함수
def save_vote_to_csv(data, file_path="votes.csv"):
    header = ["user_id", "filename", "timestamp"]
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        for row in data:
            writer.writerow(row)

# 사용자 ID 생성 (Streamlit 세션 상태에 저장)
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())  # 고유 사용자 ID 생성

# 사용자 투표 데이터 초기화
if "votes" not in st.session_state:
    st.session_state["votes"] = []

# 이미지 파일 로드
if not os.path.exists(IMAGE_DIR):
    st.error("이미지 디렉토리가 존재하지 않습니다. 'images' 폴더를 생성하고 이미지를 추가하세요.")
else:
    # 폴더 내 이미지 파일 검색
    g_files = [f for f in os.listdir(IMAGE_DIR) if f.startswith('G') and f.endswith(('jpg', 'jpeg', 'png'))]
    i_files = [f for f in os.listdir(IMAGE_DIR) if f.startswith('I') and f.endswith(('jpg', 'jpeg', 'png'))]

    if len(g_files) == 0 or len(i_files) == 0:
        st.warning("G로 시작하는 파일과 I로 시작하는 파일이 각각 1개 이상 필요합니다.")
    else:
        # 파일명에서 숫자 추출하여 정렬
        g_files.sort(key=lambda x: int(x.split('.')[1]))
        i_files.sort(key=lambda x: int(x.split('.')[1]))

        # 랜덤하게 한 쌍 선택
        pair_index = random.randint(0, min(len(g_files), len(i_files)) - 1)
        selected_files = [g_files[pair_index], i_files[pair_index]]

        # 이미지 순서를 랜덤하게 섞기
        random.shuffle(selected_files)
        image_paths = [os.path.join(IMAGE_DIR, img) for img in selected_files]

        st.title("이미지 투표")
        st.write(f"당신의 ID: **{st.session_state['user_id']}**")
        st.write("아래 두 이미지 중 하나를 선택하세요:")

        # 이미지 표시
        col1, col2 = st.columns(2)
        with col1:
            st.image(image_paths[0], caption="이미지 1", use_container_width=True)
            vote1 = st.button("이미지 1 선택")
        with col2:
            st.image(image_paths[1], caption="이미지 2", use_container_width=True)
            vote2 = st.button("이미지 2 선택")

        # 투표 결과 저장 (세션 상태에 임시 저장)
        if vote1:
            st.session_state["votes"].append([st.session_state["user_id"], selected_files[0], datetime.now().isoformat()])
            st.success(f"'{selected_files[0]}'를 선택했습니다!")
        elif vote2:
            st.session_state["votes"].append([st.session_state["user_id"], selected_files[1], datetime.now().isoformat()])
            st.success(f"'{selected_files[1]}'를 선택했습니다!")

        # 투표 종료 버튼
        if st.button("투표 종료"):
            if st.session_state["votes"]:
                save_vote_to_csv(st.session_state["votes"])
                
                # 현재 사용자의 투표 결과 분석
                total_votes = len(st.session_state["votes"])
                g_votes = sum(1 for vote in st.session_state["votes"] if vote[1].startswith('G'))
                i_votes = sum(1 for vote in st.session_state["votes"] if vote[1].startswith('I'))
                
                st.success("투표 결과가 저장되었습니다!")
                st.write("---")
                st.write("### 투표 결과 분석")
                st.write(f"- 사용자 ID: **{st.session_state['user_id']}**")
                st.write(f"- 전체 투표 횟수: **{total_votes}**회")
                st.write(f"- G 이미지 선택 횟수: **{g_votes}**회")
                st.write(f"- I 이미지 선택 횟수: **{i_votes}**회")
                
                st.session_state["votes"] = []  # 저장 후 초기화
            else:
                st.warning("저장할 투표 데이터가 없습니다.")