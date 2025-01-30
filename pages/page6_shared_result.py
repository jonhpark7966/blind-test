import streamlit as st
import os
import pandas as pd
from utils.metadata_handler import MetadataHandler
from utils.stats_handler import StatsHandler
import plotly.express as px

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

    st.write("### Shared Voting Results")
    st.write(f"Total Votes: {len(votes)}")

    # Prepare data for chart
    vote_data = []
    for vote in votes:
        vote_data.append({
            'model': vote['model'],
            'tag': vote['tag'],
            'count': 1
        })

    vote_df = pd.DataFrame(vote_data)

    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        selected_models = st.multiselect(
            "Select Models",
            options=sorted(vote_df['model'].unique()),
            default=sorted(vote_df['model'].unique())
        )
    with col2:
        selected_tags = st.multiselect(
            "Select Tags",
            options=sorted(vote_df['tag'].unique()),
            default=sorted(vote_df['tag'].unique())
        )

    # Apply filters
    filtered_df = vote_df[
        (vote_df['model'].isin(selected_models)) &
        (vote_df['tag'].isin(selected_tags))
    ]

    # Group data
    filtered_df = filtered_df.groupby(['model', 'tag'])['count'].sum().reset_index()

    if len(filtered_df) > 0:
        # Create Sunburst chart
        fig = px.sunburst(
            filtered_df,
            path=['model', 'tag'],
            values='count',
            title='Vote Distribution by Model and Tag',
        )

        # Update chart layout
        fig.update_layout(
            title_x=0.5,
            title_font_size=20,
        )

        # Update trace settings
        fig.update_traces(
            textinfo='label+text+value+percent parent',
            insidetextfont=dict(size=12)
        )

        # Display chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

def main():
    st.title("Shared Voting Results")

    # Extract query parameters
    query_params = st.experimental_get_query_params()
    contest_id = query_params.get("contest_id", [None])[0]
    session_id = query_params.get("session_id", [None])[0]

    if not contest_id or not session_id:
        st.error("Invalid link. Missing contest ID or session ID.")
        return

    display_shared_results(contest_id, session_id)

if __name__ == "__main__":
    main() 