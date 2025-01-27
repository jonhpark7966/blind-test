import streamlit as st
import uuid
from typing import List, Dict

class SessionManager:
    @staticmethod
    def init_session():
        """세션 상태를 초기화합니다."""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        if 'votes' not in st.session_state:
            st.session_state.votes = []
    
    @staticmethod
    def add_vote(contest_id: str, match_number: int, chosen_option: str):
        """투표 결과를 세션에 추가합니다."""
        vote = {
            'vote_id': str(uuid.uuid4()),
            'user_id': st.session_state.user_id,
            'session_id': st.session_state.session_id,
            'contest_id': contest_id,
            'match_number': match_number,
            'chosen_option': chosen_option
        }
        st.session_state.votes.append(vote)
        return vote
    
    @staticmethod
    def get_votes() -> List[Dict]:
        """현재 세션의 모든 투표 결과를 반환합니다."""
        return st.session_state.votes 