import os
import pandas as pd
import streamlit as st

def load_my_votes(contest_dir: str):
    """현재 세션의 투표 결과를 불러옵니다."""
    # load form votes.csv
    votes_file = os.path.join(contest_dir, "votes.csv")
    votes_df = pd.read_csv(votes_file)
    # filter by session_id, make it list
    ret = votes_df[votes_df['session_id'] == st.session_state['session_id']].to_dict(orient='records')

    # TODO: filter by user_id

    return ret 