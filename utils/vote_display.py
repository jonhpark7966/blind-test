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

    with col1:
        pie_fig = px.pie(
            names=model_counts.index,
            values=model_counts.values,
            title=f"{title_prefix}투표 결과",
            color_discrete_sequence=pastel_colors
        )
        st.plotly_chart(pie_fig)
        st.write(model_counts)

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
        st.write(tag_counts_per_model)

#    # Now place the segmented control below the charts
#    new_selection = st.session_state["selected_tags"]
#    
#    # If the user changes selections, update session_state and rerun
#    if new_selection != st.session_state["selected_tags"]:
#        st.session_state["selected_tags"] = new_selection
#        st.rerun()


def get_funny_vote_message(model_count: pd.DataFrame) -> str:
    # 모델명과 투표 수를 딕셔너리 형태로 가져오기
    count_dict = dict(zip(model_count.index, model_count.values))
    
    # 투표 수 꺼내기 (없으면 0)
    s25_count = count_dict.get('Galaxy S25 Ultra', 0)
    iphone_count = count_dict.get('iPhone 16 Pro Max', 0)
    total = s25_count + iphone_count
    
    # 투표가 없는 경우
    if total == 0:
        return "아직 투표가 없습니다! 첫 표의 주인공이 되어주세요."

    # 비율 계산
    ratio_s25 = s25_count / total
    
    # 재미있는 문구 분기
    if abs(ratio_s25 - 0.5) < 0.05:
        return "🤝 완벽한 균형! 타노스도 울고 갈 50:50 매치였네요!"
    elif ratio_s25 > 0.8:
        return "🌌 갤럭시의 압도적 승리! S25 Ultra가 은하수를 지배했습니다! ✨"
    elif ratio_s25 > 0.6:
        return "🚀 S25 Ultra 진영의 승리! 우주 정복이 눈앞이네요~"
    elif ratio_s25 > 0.5:
        return "💫 갤럭시가 살짝 앞서가는 중! 아이폰, 이대로 물러설 텐가?"
    elif ratio_s25 < 0.2:
        return "🍎 아이폰의 완승! 16 Pro Max가 신의 영역을 보여줬습니다!"
    elif ratio_s25 < 0.4:
        return "📱 아이폰 16 Pro Max의 화려한 승리! 이게 바로 사과의 품격 ✨"
    else:
        return "🎯 아이폰이 근소하게 앞서는 중! "

def display_vote_results(vote_data, title_prefix=""):
    filtered_df, model_counts, unique_tags, tag_counts_per_model = filter_and_count_by_tags(vote_data)

    headline =  get_funny_vote_message(model_count=model_counts)
    st.markdown(f"{headline}\n---\n")

    display_charts(model_counts, tag_counts_per_model, title_prefix) 