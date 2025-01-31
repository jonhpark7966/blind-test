import ast
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from functools import reduce
import streamlit as st

def display_vote_results(vote_data, title_prefix=""):
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

    col1, col2 = st.columns(2)
    pastel_colors = ['#BA55D3','#FFD700','#FFB6C1', '#FF69B4']

    with col1:
        model_counts = filtered_df['model'].value_counts()
        pie_fig = px.pie(
            names=model_counts.index,
            values=model_counts.values,
            title=f"{title_prefix}투표 결과",
            color_discrete_sequence=pastel_colors
        )
        st.plotly_chart(pie_fig)

    with col2:
        bar_data = []
        for i, model in enumerate(filtered_df['model'].unique()):
            model_filtered_df = filtered_df[filtered_df['model'] == model]
            tag_counts = model_filtered_df['tags'].explode().value_counts()
            bar_data.append(
                go.Bar(
                    x=tag_counts.index,
                    y=tag_counts.values,
                    name=model,
                    marker_color=pastel_colors[i % len(pastel_colors)]
                )
            )
        bar_fig = go.Figure(data=bar_data)
        bar_fig.update_layout(barmode='group', title=f"{title_prefix}카테고리별 투표 결과")
        st.plotly_chart(bar_fig)

    # Now place the segmented control below the charts
    new_selection = st.segmented_control(
        "태그 선택",
        sorted(unique_tags),
        selection_mode="multi",
        default=default_selected_tags
    )
    # If the user changes selections, update session_state and rerun
    if new_selection != default_selected_tags:
        st.session_state["selected_tags"] = new_selection
        st.rerun() 