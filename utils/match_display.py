from pandas import Series
import streamlit as st
import os
from utils.media_handler import display_media, load_media
from utils.tag_styler import display_tags
from utils.metadata_handler import MetadataHandler

def display_total_match_result(metadata_handler: MetadataHandler, vote:Series, index:int):
    # 가장 높은 투표값을 받은 모델 찾기
    chosen_model = vote.idxmax()
    
    # 전체 매치 메타데이터
    matches = metadata_handler.get_matches()
    selected_match = [match for match in matches if match['Match'] == index]


    border_colors = []
    medias = []
    models = []

    for data in selected_match:
        filename = data['FileName']
        model = data.get('Model')
        tags = data.get('tags', [])

        # File path
        file_path = os.path.join(metadata_handler.directory, filename)

        # Border style based on selection
        border_colors.append("green" if model == chosen_model else "gray")
        models.append(model)
        medias.append(load_media(file_path, metadata_handler))

    with st.container():
        # view match number and tags  
        # also add a total vote count  
        st.write(f"### Match {index}")
        st.write(f"총 투표 수: {vote.sum()}회")
        display_tags(tags)
        col1, col2 = st.columns(2)

        # Determine which media should be in col1 based on selection
        if model == next(iter(metadata_handler.get_unique_models())):
            first_media_index = 0
            second_media_index = 1
        else:
            first_media_index = 1
            second_media_index = 0

        with col1:
            # show model name, vote count, and media with border color
            border_width = "3px"  # Increase border width
            model_name = models[first_media_index]
            vote_count = vote[model_name]
            check_icon = "✅" if border_colors[first_media_index] == "green" else ""
            st.markdown(f"<div style='border: {border_width} solid {border_colors[first_media_index]}; padding: 10px;'>"
                        f"<div style='color: {border_colors[first_media_index]};'>{model_name} ({vote_count}회) {check_icon}</div>", unsafe_allow_html=True)
            display_media(col1, medias[first_media_index])

        with col2:
            # show model name, vote count, and media with border color
            border_width = "3px"  # Increase border width
            model_name = models[second_media_index]
            vote_count = vote[model_name]
            check_icon = "✅" if border_colors[second_media_index] == "green" else ""
            st.markdown(f"<div style='border: {border_width} solid {border_colors[second_media_index]}; padding: 10px;'>"
                        f"<div style='color: {border_colors[second_media_index]};'>{model_name} ({vote_count}회) {check_icon}</div>", unsafe_allow_html=True)
            display_media(col2, medias[second_media_index])
    


def display_match_result(metadata_handler: MetadataHandler, match_number: int, chosen_option: str, index: int):
    """Display the result of a match visually."""
    match_data = metadata_handler.get_matches()

    # Display images/videos
    border_colors = []
    medias = []
    models = []
    for data in match_data:
        # filter by match number 
        if data['Match'] != match_number:
            continue

        filename = data['FileName']
        model = data.get('Model', '')
        tags = data.get('tags', [])

        # File path
        file_path = os.path.join(metadata_handler.directory, filename)

        # Border style based on selection
        border_colors.append("green" if filename == chosen_option else "gray")
        models.append(model)
        medias.append(load_media(file_path, metadata_handler))

    with st.container():
        # view match number and tags    
        st.write(f"### Match {index}")
        display_tags(tags)
        col1, col2 = st.columns(2)

        # Determine which media should be in col1 based on selection
        if model == next(iter(metadata_handler.get_unique_models())):
            first_media_index = 0
            second_media_index = 1
        else:
            first_media_index = 1
            second_media_index = 0

        with col1:
            # show model name, vote count, and media with border color
            border_width = "3px"  # Increase border width
            model_name = models[first_media_index]
            check_icon = "✅" if border_colors[first_media_index] == "green" else ""
            st.markdown(f"<div style='border: {border_width} solid {border_colors[first_media_index]}; padding: 10px;'>"
                        f"<div style='color: {border_colors[first_media_index]};'>{model_name} {check_icon}</div>", unsafe_allow_html=True)
            display_media(col1, medias[first_media_index])

        with col2:
            # show model name, vote count, and media with border color
            border_width = "3px"  # Increase border width
            model_name = models[second_media_index]
            check_icon = "✅" if border_colors[second_media_index] == "green" else ""
            st.markdown(f"<div style='border: {border_width} solid {border_colors[second_media_index]}; padding: 10px;'>"
                        f"<div style='color: {border_colors[second_media_index]};'>{model_name} {check_icon}</div>", unsafe_allow_html=True)
            display_media(col2, medias[second_media_index])

def display_pagination(total_pages):
    col1, col2, col3 = st.columns(3, gap="large")

    def prev_page():
        if st.session_state.page_number > 1:
            st.session_state.page_number -= 1

    def next_page():
        if st.session_state.page_number < total_pages:
            st.session_state.page_number += 1
    
    with col1:
        st.button("⬅", on_click=prev_page, use_container_width=True, key='prev_page_button')

    with col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 20px;'>"
            f"Page {st.session_state.page_number} of {total_pages}"
            f"</div>",
            unsafe_allow_html=True)

    with col3:
        st.button("➡", on_click=next_page, use_container_width=True) 