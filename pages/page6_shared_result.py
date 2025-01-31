import ast
from functools import reduce
import streamlit as st
import os
import pandas as pd
from utils.metadata_handler import MetadataHandler
from utils.stats_handler import StatsHandler
import plotly.express as px
import plotly.graph_objects as go
from utils.vote_display import display_vote_results

def load_shared_votes(contest_id: str, session_id: str):
    """Load votes for a specific session ID."""
    contest_dir = os.path.join("data", "contests", contest_id)
    votes_file = os.path.join(contest_dir, "votes.csv")
    votes_df = pd.read_csv(votes_file)
    return votes_df[votes_df['session_id'] == session_id].to_dict(orient='records')

def display_shared_results(contest_id: str, session_id: str):
    """Display the results for the shared session."""
    # Load all contests for the session
    all_contests = MetadataHandler.get_contests_for_session(session_id)
    
    # Sidebar for contest selection
    selected_contest_name = st.sidebar.selectbox(
        "Select Contest",
        options=[contest['name'] for contest in all_contests],
        index=next(i for i, contest in enumerate(all_contests) if contest['contest_id'] == contest_id)
    )

    # Find the selected contest dictionary
    selected_contest = next(contest for contest in all_contests if contest['name'] == selected_contest_name)

    # Load votes for the selected contest
    selected_contest_id = selected_contest['contest_id']
    votes = load_shared_votes(selected_contest_id, session_id)
    if not votes:
        st.write("No results found for this session.")
        return

    st.write("### 공유된 투표 결과")
    st.write(f"전체 투표 횟수: {len(votes)}회")
    
    display_vote_results(votes, title_prefix="공유된 ")

def main():
    st.title("Shared Voting Results")

    # Extract query parameters
    contest_id = st.query_params["contest_id"]
    session_id = st.query_params["session_id"]

    if not contest_id or not session_id:
        st.error("Invalid link. Missing contest ID or session ID.")
        return

    display_shared_results(contest_id, session_id)

if __name__ == "__main__":
    main() 