import streamlit as st

# Markdown 파일 읽기
with open("README.md", "r", encoding="utf-8") as file:
    readme_content = file.read()

# Streamlit에서 Markdown 파일 표시
st.title("📄 README Viewer")
st.markdown(readme_content, unsafe_allow_html=True)