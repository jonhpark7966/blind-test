import streamlit as st
import os
import sys

from utils.contest_sidebar import display_contest_sidebar, display_page_sidebar_with_page
from utils.stats_handler import process_all_contest_dirs

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

base_directory = os.path.join('data', 'contests')  # 각 contest 디렉토리가 있는 상위 디렉토리 경로

# 모든 콘테스트 디렉토리 처리
# 매 5분마다 process 따로 생성해서 돌리기
import threading
import time

def run_process_periodically():
    while True:
        process_all_contest_dirs(base_directory)
        time.sleep(300)  # 5 minutes in seconds

# Create and start a separate thread for the periodic process
thread = threading.Thread(target=run_process_periodically)
thread.start()

st.set_option("client.showSidebarNavigation", False)
# Page configuration
st.set_page_config(
    page_title="블라인드 테스트",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state if needed
if "votes" not in st.session_state:
    st.session_state.votes = []

display_contest_sidebar()

st.switch_page("pages/vote.py")