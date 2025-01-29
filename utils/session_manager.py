import streamlit as st
import uuid
from typing import List, Dict
import pandas as pd
import os
from datetime import datetime

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
    def add_vote(contest_id: str, match_number: int, chosen_option: str, tag: str = ""):
        """투표 결과를 세션에 추가합니다."""
        vote = {
            'vote_id': str(uuid.uuid4()),
            'user_id': st.session_state.user_id,
            'session_id': st.session_state.session_id,
            'contest_id': contest_id,
            'match_number': match_number,
            'chosen_option': chosen_option,
            'tag': tag
        }
        st.session_state.votes.append(vote)
        return vote
    
    @staticmethod
    def get_votes() -> List[Dict]:
        """현재 세션의 모든 투표 결과를 반환합니다."""
        return st.session_state.votes 

    @staticmethod
    def save_votes(votes: List[Dict]):
        """투표 내역을 각 contest의 votes.csv에 저장한다."""
        # votes가 비어있으면 저장하지 않음
        if not votes:
            return
        
        # 컨테스트별로 투표 분류
        votes_by_contest = {}
        for vote in votes:
            contest_id = vote['contest_id']
            contest_dir = vote['contest_dir']
            if contest_id not in votes_by_contest:
                votes_by_contest[contest_id] = {
                    'votes': [],
                    'dir': contest_dir
                }
            votes_by_contest[contest_id]['votes'].append(vote)

        # 각 컨테스트별로 votes.csv 저장
        for contest_id, contest_data in votes_by_contest.items():
            contest_dir = contest_data['dir']
            contest_votes = contest_data['votes']
            
            votes_file = os.path.join(contest_dir, "votes.csv")
            if os.path.exists(votes_file):
                old_df = pd.read_csv(votes_file)
            else:
                old_df = pd.DataFrame(columns=[
                    "vote_id", "user_id", "session_id", "contest_id",
                    "match_number", "chosen_option", "model", "timestamp", "tag"
                ])

            metadata_handler = st.session_state.metadata_handlers[contest_id]
            metadata = metadata_handler.get_matches()

            new_rows = []
            for v in contest_votes:
                # Find model info from metadata
                chosen_file = v['selected']
                chosen_metadata = next((m for m in metadata if m['FileName'] == chosen_file), None)
                model = chosen_metadata.get('Model', '') if chosen_metadata else ''
                tag = chosen_metadata.get('tag', '') if chosen_metadata else ''

                new_rows.append({
                    "vote_id": str(uuid.uuid4()),
                    "user_id": "anonymous",  # TODO: 실제로는 계정 시스템과 연동
                    "session_id": st.session_state["session_id"],
                    "contest_id": contest_id,
                    "match_number": v['match_number'],
                    "chosen_option": v['selected'],
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "tag": tag  # 태그가 없는 경우 빈 문자열 사용
                })
            
            new_df = pd.DataFrame(new_rows)
            final_df = pd.concat([old_df, new_df], ignore_index=True)
            final_df.to_csv(votes_file, index=False) 

    @staticmethod
    def save_votes_and_reset():
        """투표 내역을 저장하고 세션의 votes를 초기화합니다."""
        if 'votes' in st.session_state and st.session_state.votes:
            votes = st.session_state.votes
            SessionManager.save_votes(votes)
            num_votes = len(votes)
            st.session_state.votes = []
            return num_votes
        return 0 