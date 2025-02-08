import ast
from functools import reduce
import os
import pandas as pd
import streamlit as st

def load_shared_votes(contest_id: str, session_id: str):
    """Load votes for a specific session ID."""
    contest_dir = os.path.join("data", "contests", contest_id)
    votes_file = os.path.join(contest_dir, "votes.csv")
    votes_df = pd.read_csv(votes_file)
    return votes_df[votes_df['session_id'] == session_id].to_dict(orient='records')

def load_my_votes(contest_dir: str):
    """현재 세션의 투표 결과를 불러옵니다."""
    # load form votes.csv
    votes_file = os.path.join(contest_dir, "votes.csv")
    votes_df = pd.read_csv(votes_file)
    # filter by session_id, make it list
    ret = votes_df[votes_df['session_id'] == st.session_state['session_id']].to_dict(orient='records')

    # TODO: filter by user_id

    return ret 

def load_total_votes(contest_dir: str):
    """전체 투표 결과를 불러옵니다."""
    votes_file = os.path.join(contest_dir, "votes.csv")
    votes = pd.read_csv(votes_file).to_dict(orient='records')
    return votes

def filter_and_count_by_tags(vote_data):
    vote_df = pd.DataFrame(vote_data)
    vote_df['tags'] = vote_df['tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    # Collect all unique tags
    unique_tags = set()
    for tags in vote_df['tags']:
        for tag in tags:
            unique_tags.add(tag)

    # By default we use all tags (or the previously selected ones, if any)
    if "selected_tags" not in st.session_state:
        st.session_state["selected_tags"] = sorted(unique_tags)
    default_selected_tags = st.session_state["selected_tags"]

    # First, filter the dataframe based on the currently selected tags
    conditions = []
    for tag in default_selected_tags:
        conditions.append(vote_df['tags'].apply(lambda x: tag in x))
    filtered_df = vote_df[reduce(lambda x, y: x | y, conditions)] if conditions else vote_df

    # add index to model_counts
    model_counts = filtered_df['model'].value_counts()

    # Calculate tag counts per model
    tag_counts_per_model = {}
    for model in filtered_df['model'].unique():
        model_filtered_df = filtered_df[filtered_df['model'] == model]
        tag_counts = model_filtered_df['tags'].explode().value_counts()
        tag_counts_per_model[model] = tag_counts

    return filtered_df, model_counts, unique_tags, tag_counts_per_model