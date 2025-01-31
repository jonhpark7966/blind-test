import ast
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from functools import reduce
import streamlit as st
from utils.votes_handler import filter_and_count_by_tags


def display_charts(model_counts, tag_counts_per_model, title_prefix=""):
    col1, col2 = st.columns(2)
    pastel_colors = ['#BA55D3','#FFD700','#FFB6C1', '#FF69B4']

    st.write(model_counts)
    st.write(tag_counts_per_model)

    with col1:
        pie_fig = px.pie(
            names=model_counts.index,
            values=model_counts.values,
            title=f"{title_prefix}투표 결과",
            color_discrete_sequence=pastel_colors
        )
        st.plotly_chart(pie_fig)

    with col2:
        bar_data = []
        for i, model in enumerate(model_counts.index):
            tag_counts = tag_counts_per_model[model]
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
    new_selection = st.session_state["selected_tags"]
    
    # If the user changes selections, update session_state and rerun
    if new_selection != st.session_state["selected_tags"]:
        st.session_state["selected_tags"] = new_selection
        st.rerun()

def display_vote_results(vote_data, title_prefix=""):
    filtered_df, model_counts, unique_tags, tag_counts_per_model = filter_and_count_by_tags(vote_data)
    display_charts(model_counts, tag_counts_per_model, title_prefix) 